import pandas as pd
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv()

def get_engine():
    url = os.getenv('DW_DATABASE_URL', 'sqlite:///instance/dw_hospitality.db')
    if url.startswith('sqlite'):
        return create_engine(url)
    return create_engine( # type: ignore
        url,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=10,
        connect_args={"connect_timeout": 10}
    )

def _build_filters(year=None, hotel_type=None, channel=None):
    c = []
    if year:       c.append(f"t.year = {int(year)}")
    if hotel_type: c.append(f"h.hotel_type = '{hotel_type}'")
    if channel:    c.append(f"c.channel_name = '{channel}'")
    return "WHERE " + " AND ".join(c) if c else ""

def get_filter_options():
    engine = get_engine()
    years    = pd.read_sql("SELECT DISTINCT year FROM dim_time ORDER BY year", engine)['year'].tolist()
    htypes   = pd.read_sql("SELECT DISTINCT hotel_type FROM dim_hotel ORDER BY hotel_type", engine)['hotel_type'].tolist()
    channels = pd.read_sql("SELECT DISTINCT channel_name FROM dim_booking_channel ORDER BY channel_name", engine)['channel_name'].tolist()
    return {'years': years, 'hotel_types': htypes, 'channels': channels}

def get_kpi_stats(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    q = f"""
    SELECT COUNT(f.reservation_key) AS total_reservasi,
        SUM(CASE WHEN f.is_cancelled='No' THEN f.room_revenue ELSE 0 END) AS total_revenue,
        SUM(CASE WHEN f.is_cancelled='No' THEN f.nights ELSE 0 END)
            / NULLIF(SUM(CASE WHEN f.is_cancelled='No' THEN 1 ELSE 0 END),0) AS avg_nights,
        COUNT(DISTINCT f.guest_key) AS total_tamu,
        SUM(CASE WHEN f.is_cancelled='Yes' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(f.reservation_key),0) * 100 AS cancel_rate
    FROM fact_reservation f
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {f}"""
    row = pd.read_sql(q, engine).iloc[0]
    return {
        'total_reservasi': int(row['total_reservasi'] or 0),
        'total_revenue':   float(row['total_revenue'] or 0),
        'avg_nights':      round(float(row['avg_nights'] or 0), 1),
        'total_tamu':      int(row['total_tamu'] or 0),
        'cancel_rate':     round(float(row['cancel_rate'] or 0), 1),
    }

def get_occupancy_by_quarter(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT t.year, t.quarter, h.hotel_type,
        COUNT(f.reservation_key) AS total_reservasi,
        SUM(f.rooms_booked) AS total_kamar,
        SUM(f.room_revenue) AS total_revenue
    FROM fact_reservation f
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra}
    GROUP BY t.year, t.quarter, h.hotel_type ORDER BY t.year, t.quarter"""
    df = pd.read_sql(q, engine)
    result = {}
    for ht in df['hotel_type'].unique():
        sub = df[df['hotel_type']==ht].sort_values(['year','quarter'])
        result[ht] = {
            'labels':    [f"Q{r['quarter']} {r['year']}" for _,r in sub.iterrows()],
            'revenue':   [round(float(v),0) for v in sub['total_revenue']],
            'reservasi': [int(v) for v in sub['total_reservasi']],
        }
    return result

def get_channel_distribution(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    q = f"""
    SELECT c.channel_name, c.channel_type,
        COUNT(f.reservation_key) AS total, SUM(f.room_revenue) AS revenue
    FROM fact_reservation f
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_time t ON f.date_key = t.date_key
    {f} GROUP BY c.channel_name, c.channel_type ORDER BY total DESC"""
    df = pd.read_sql(q, engine)
    return {'labels': df['channel_name'].tolist(),
            'values': [int(v) for v in df['total']],
            'revenue':[round(float(v),0) for v in df['revenue']]}

def get_guest_segment(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT g.segment, COUNT(f.reservation_key) AS total
    FROM fact_reservation f
    JOIN dim_guest g ON f.guest_key = g.guest_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra} GROUP BY g.segment ORDER BY total DESC"""
    df = pd.read_sql(q, engine)
    return {'labels': df['segment'].tolist(), 'values': [int(v) for v in df['total']]}

def get_nationality(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT g.nationality, COUNT(f.reservation_key) AS total
    FROM fact_reservation f
    JOIN dim_guest g ON f.guest_key = g.guest_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra} GROUP BY g.nationality ORDER BY total DESC LIMIT 8"""
    df = pd.read_sql(q, engine)
    return {'labels': df['nationality'].tolist(), 'values': [int(v) for v in df['total']]}

def get_hotel_revenue(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT h.hotel_name, h.hotel_type, h.city, h.star_rating,
        COUNT(f.reservation_key) AS total_reservasi,
        SUM(f.room_revenue) AS total_revenue,
        AVG(f.nights) AS avg_nights
    FROM fact_reservation f
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra}
    GROUP BY h.hotel_key, h.hotel_name, h.hotel_type, h.city, h.star_rating
    ORDER BY total_revenue DESC"""
    df = pd.read_sql(q, engine)
    return {
        'labels':    df['hotel_name'].tolist(),
        'revenue':   [round(float(v),0) for v in df['total_revenue']],
        'reservasi': [int(v) for v in df['total_reservasi']],
        'detail':    df.to_dict('records'),
    }

def get_room_type(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT r.room_type, COUNT(f.reservation_key) AS total,
        SUM(f.room_revenue) AS revenue, AVG(r.base_rate) AS avg_rate
    FROM fact_reservation f
    JOIN dim_room r ON f.room_key = r.room_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra} GROUP BY r.room_type ORDER BY total DESC"""
    df = pd.read_sql(q, engine)
    return {'labels': df['room_type'].tolist(),
            'values': [int(v) for v in df['total']],
            'revenue':[round(float(v),0) for v in df['revenue']]}

def get_seasonal_trend(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT t.year, t.quarter,
        COUNT(f.reservation_key) AS total_reservasi,
        SUM(f.room_revenue) AS total_revenue,
        AVG(f.nights) AS avg_nights
    FROM fact_reservation f
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra} GROUP BY t.year, t.quarter ORDER BY t.year, t.quarter"""
    df = pd.read_sql(q, engine)
    return {
        'labels':    [f"Q{r['quarter']} {r['year']}" for _,r in df.iterrows()],
        'reservasi': [int(v) for v in df['total_reservasi']],
        'revenue':   [round(float(v),0) for v in df['total_revenue']],
        'avg_nights':[round(float(v),1) for v in df['avg_nights']],
    }

def get_okupansi_detail(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT h.hotel_key, h.hotel_name, h.hotel_type, h.city, t.year, t.quarter,
        COUNT(f.reservation_key) AS total_reservasi,
        SUM(f.rooms_booked) AS total_kamar,
        SUM(f.room_revenue) AS total_revenue,
        AVG(f.nights) AS avg_nights,
        SUM(CASE WHEN f.is_cancelled='Yes' THEN 1 ELSE 0 END) AS total_batal
    FROM fact_reservation f
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra}
    GROUP BY h.hotel_key,h.hotel_name,h.hotel_type,h.city,t.year,t.quarter
    ORDER BY t.year, t.quarter, total_revenue DESC"""
    return pd.read_sql(q, engine).to_dict('records')

def get_customer_detail(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT g.guest_key, g.guest_name, g.nationality, g.segment, g.city,
        COUNT(f.reservation_key) AS total_booking,
        SUM(f.nights) AS total_malam,
        SUM(f.room_revenue) AS total_spend,
        AVG(f.room_revenue) AS avg_spend
    FROM fact_reservation f
    JOIN dim_guest g ON f.guest_key = g.guest_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra}
    GROUP BY g.guest_key,g.guest_name,g.nationality,g.segment,g.city
    ORDER BY total_spend DESC LIMIT 100"""
    return pd.read_sql(q, engine).to_dict('records')

def get_room_detail(year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    base = f if f else "WHERE f.is_cancelled='No'"
    extra = " AND f.is_cancelled='No'" if f else ""
    q = f"""
    SELECT r.room_key, r.room_type, r.capacity, r.base_rate,
        h.hotel_name, h.hotel_type,
        COUNT(f.reservation_key) AS total_booking,
        SUM(f.rooms_booked) AS total_kamar_terjual,
        SUM(f.room_revenue) AS total_revenue,
        AVG(f.nights) AS avg_nights
    FROM fact_reservation f
    JOIN dim_room r ON f.room_key = r.room_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {base}{extra}
    GROUP BY r.room_key,r.room_type,r.capacity,r.base_rate,h.hotel_name,h.hotel_type
    ORDER BY total_revenue DESC"""
    return pd.read_sql(q, engine).to_dict('records')

def get_recent_reservations(limit=10):
    engine = get_engine()
    q = f"""
    SELECT f.reservation_key, g.guest_name, h.hotel_name,
        r.room_type, c.channel_name, f.nights,
        f.rooms_booked, f.room_revenue, f.is_cancelled, t.date AS tanggal
    FROM fact_reservation f
    JOIN dim_guest g ON f.guest_key = g.guest_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_room r ON f.room_key = r.room_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    JOIN dim_time t ON f.date_key = t.date_key
    ORDER BY f.reservation_key DESC LIMIT {limit}"""
    return pd.read_sql(q, engine).to_dict('records')

def get_export_data(tipe='reservasi', year=None, hotel_type=None, channel=None):
    engine = get_engine()
    f = _build_filters(year, hotel_type, channel)
    if tipe == 'reservasi':
        q = f"""
        SELECT f.reservation_key AS 'ID', g.guest_name AS 'Nama Tamu',
            g.nationality AS 'Negara', g.segment AS 'Segmen',
            h.hotel_name AS 'Hotel', h.hotel_type AS 'Tipe Hotel',
            r.room_type AS 'Tipe Kamar', c.channel_name AS 'Channel',
            t.year AS 'Tahun', t.quarter AS 'Kuartal',
            f.nights AS 'Malam', f.rooms_booked AS 'Kamar',
            f.room_revenue AS 'Revenue', f.is_cancelled AS 'Batal'
        FROM fact_reservation f
        JOIN dim_guest g ON f.guest_key=g.guest_key
        JOIN dim_hotel h ON f.hotel_key=h.hotel_key
        JOIN dim_room r ON f.room_key=r.room_key
        JOIN dim_booking_channel c ON f.channel_key=c.channel_key
        JOIN dim_time t ON f.date_key=t.date_key {f}
        ORDER BY f.reservation_key DESC"""
    elif tipe == 'okupansi':
        base = f if f else "WHERE f.is_cancelled='No'"
        extra = " AND f.is_cancelled='No'" if f else ""
        q = f"""
        SELECT h.hotel_name AS 'Hotel', h.hotel_type AS 'Tipe', h.city AS 'Kota',
            t.year AS 'Tahun', t.quarter AS 'Kuartal',
            COUNT(f.reservation_key) AS 'Total Reservasi',
            SUM(f.rooms_booked) AS 'Total Kamar',
            SUM(f.room_revenue) AS 'Total Revenue'
        FROM fact_reservation f
        JOIN dim_hotel h ON f.hotel_key=h.hotel_key
        JOIN dim_time t ON f.date_key=t.date_key
        JOIN dim_booking_channel c ON f.channel_key=c.channel_key
        {base}{extra}
        GROUP BY h.hotel_key,h.hotel_name,h.hotel_type,h.city,t.year,t.quarter"""
    elif tipe == 'customer':
        base = f if f else "WHERE f.is_cancelled='No'"
        extra = " AND f.is_cancelled='No'" if f else ""
        q = f"""
        SELECT g.guest_name AS 'Nama', g.nationality AS 'Negara',
            g.segment AS 'Segmen', g.city AS 'Kota',
            COUNT(f.reservation_key) AS 'Total Booking',
            SUM(f.nights) AS 'Total Malam',
            SUM(f.room_revenue) AS 'Total Spend'
        FROM fact_reservation f
        JOIN dim_guest g ON f.guest_key=g.guest_key
        JOIN dim_hotel h ON f.hotel_key=h.hotel_key
        JOIN dim_time t ON f.date_key=t.date_key
        JOIN dim_booking_channel c ON f.channel_key=c.channel_key
        {base}{extra}
        GROUP BY g.guest_key,g.guest_name,g.nationality,g.segment,g.city
        ORDER BY 7 DESC"""
    return pd.read_sql(q, engine)


# ── OLAP CORE CONFIGURATION & PARAMS ──
ALLOWED_DIMENSIONS = {
    'year': 't.year',
    'quarter': 't.quarter',
    'month_name': 't.month_name',
    'is_weekend': 't.is_weekend',
    'hotel_name': 'h.hotel_name',
    'hotel_type': 'h.hotel_type',
    'city': 'h.city',
    'star_rating': 'h.star_rating',
    'room_type': 'r.room_type',
    'channel_name': 'c.channel_name',
    'channel_type': 'c.channel_type',
    'nationality': 'g.nationality',
    'segment': 'g.segment',
    'is_cancelled': 'f.is_cancelled'
}

DIMENSION_LABELS = {
    'year': 'Tahun',
    'quarter': 'Kuartal',
    'month_name': 'Bulan',
    'is_weekend': 'Weekend (Yes/No)',
    'hotel_name': 'Nama Hotel',
    'hotel_type': 'Tipe Hotel',
    'city': 'Kota',
    'star_rating': 'Rating Bintang',
    'room_type': 'Tipe Kamar',
    'channel_name': 'Channel Booking',
    'channel_type': 'Tipe Channel',
    'nationality': 'Negara Asal',
    'segment': 'Segmen Tamu',
    'is_cancelled': 'Status Batal'
}

ALLOWED_MEASURES = {
    'total_reservasi': 'COUNT(f.reservation_key) AS total_reservasi',
    'total_revenue': 'SUM(CASE WHEN f.is_cancelled="No" THEN f.room_revenue ELSE 0 END) AS total_revenue',
    'total_rooms_booked': 'SUM(CASE WHEN f.is_cancelled="No" THEN f.rooms_booked ELSE 0 END) AS total_rooms_booked',
    'avg_nights': 'SUM(CASE WHEN f.is_cancelled="No" THEN f.nights ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_cancelled="No" THEN 1 ELSE 0 END), 0) AS avg_nights',
    'avg_spend': 'SUM(CASE WHEN f.is_cancelled="No" THEN f.room_revenue ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_cancelled="No" THEN 1 ELSE 0 END), 0) AS avg_spend',
    'cancel_rate': 'SUM(CASE WHEN f.is_cancelled="Yes" THEN 1 ELSE 0 END) / NULLIF(COUNT(f.reservation_key), 0) * 100 AS cancel_rate'
}

MEASURE_LABELS = {
    'total_reservasi': 'Total Reservasi',
    'total_revenue': 'Total Revenue',
    'total_rooms_booked': 'Total Kamar Terjual',
    'avg_nights': 'Rata-rata Malam',
    'avg_spend': 'Rata-rata Spend',
    'cancel_rate': 'Cancellation Rate (%)'
}

def get_all_filter_options():
    engine = get_engine()
    years = pd.read_sql("SELECT DISTINCT year FROM dim_time ORDER BY year", engine)['year'].tolist()
    quarters = pd.read_sql("SELECT DISTINCT quarter FROM dim_time ORDER BY quarter", engine)['quarter'].tolist()
    months = pd.read_sql("SELECT DISTINCT month_name FROM dim_time ORDER BY month_name", engine)['month_name'].tolist()
    weekends = pd.read_sql("SELECT DISTINCT is_weekend FROM dim_time ORDER BY is_weekend", engine)['is_weekend'].tolist()
    
    hotel_names = pd.read_sql("SELECT DISTINCT hotel_name FROM dim_hotel ORDER BY hotel_name", engine)['hotel_name'].tolist()
    hotel_types = pd.read_sql("SELECT DISTINCT hotel_type FROM dim_hotel ORDER BY hotel_type", engine)['hotel_type'].tolist()
    cities = pd.read_sql("SELECT DISTINCT city FROM dim_hotel ORDER BY city", engine)['city'].tolist()
    star_ratings = pd.read_sql("SELECT DISTINCT star_rating FROM dim_hotel ORDER BY star_rating", engine)['star_rating'].tolist()
    
    room_types = pd.read_sql("SELECT DISTINCT room_type FROM dim_room ORDER BY room_type", engine)['room_type'].tolist()
    
    segments = pd.read_sql("SELECT DISTINCT segment FROM dim_guest ORDER BY segment", engine)['segment'].tolist()
    nationalities = pd.read_sql("SELECT DISTINCT nationality FROM dim_guest ORDER BY nationality", engine)['nationality'].tolist()
    
    channels = pd.read_sql("SELECT DISTINCT channel_name FROM dim_booking_channel ORDER BY channel_name", engine)['channel_name'].tolist()
    channel_types = pd.read_sql("SELECT DISTINCT channel_type FROM dim_booking_channel ORDER BY channel_type", engine)['channel_type'].tolist()
    
    return {
        'years': [str(y) for y in years],
        'quarters': [str(q) for q in quarters],
        'months': months,
        'weekends': weekends,
        'hotel_names': hotel_names,
        'hotel_types': hotel_types,
        'cities': cities,
        'star_ratings': [str(s) for s in star_ratings],
        'room_types': room_types,
        'segments': segments,
        'nationalities': nationalities,
        'channels': channels,
        'channel_types': channel_types
    }

# pyrefly: ignore [missing-import]
from sqlalchemy import text

def run_olap_query(dimensions, measures, filters=None):
    if not dimensions:
        dimensions = ['year']
    if not measures:
        measures = ['total_reservasi', 'total_revenue']
        
    select_items = []
    group_by_items = []
    
    for d in dimensions:
        if d in ALLOWED_DIMENSIONS:
            col = ALLOWED_DIMENSIONS[d]
            select_items.append(f"{col} AS `{d}`")
            group_by_items.append(col)
            
    for m in measures:
        if m in ALLOWED_MEASURES:
            select_items.append(ALLOWED_MEASURES[m])
            
    select_clause = ", ".join(select_items)
    
    where_parts = []
    params = {}
    
    if filters:
        for fk, fvals in filters.items():
            if fk in ALLOWED_DIMENSIONS and fvals:
                col = ALLOWED_DIMENSIONS[fk]
                # normalize fvals to a list if not already
                if not isinstance(fvals, list):
                    fvals = [fvals]
                # remove empty string values
                fvals = [v for v in fvals if v != '']
                if fvals:
                    placeholders = []
                    for idx, val in enumerate(fvals):
                        param_name = f"filter_{fk}_{idx}"
                        placeholders.append(f":{param_name}")
                        if fk in ['year', 'quarter', 'star_rating']:
                            try:
                                params[param_name] = int(val)
                            except ValueError:
                                params[param_name] = val
                        else:
                            params[param_name] = str(val)
                    where_parts.append(f"{col} IN ({', '.join(placeholders)})")
                    
    where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
    group_by_clause = "GROUP BY " + ", ".join(group_by_items) if group_by_items else ""
    order_by_clause = "ORDER BY " + ", ".join(group_by_items) if group_by_items else ""
    
    sql = f"""
    SELECT {select_clause}
    FROM fact_reservation f
    JOIN dim_time t ON f.date_key = t.date_key
    JOIN dim_hotel h ON f.hotel_key = h.hotel_key
    JOIN dim_room r ON f.room_key = r.room_key
    JOIN dim_guest g ON f.guest_key = g.guest_key
    JOIN dim_booking_channel c ON f.channel_key = c.channel_key
    {where_clause}
    {group_by_clause}
    {order_by_clause}
    """
    
    engine = get_engine()
    df = pd.read_sql(text(sql), engine, params=params)
    return df

