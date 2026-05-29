import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

def get_engine():
    url = os.getenv('DW_DATABASE_URL', 'mysql+pymysql://root:@localhost/dw_hospitality')
    return create_engine(
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
    SELECT h.hotel_name, h.hotel_type, h.city, t.year, t.quarter,
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
    SELECT g.guest_name, g.nationality, g.segment, g.city,
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
    SELECT r.room_type, r.capacity, r.base_rate,
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
