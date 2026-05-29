# pyrefly: ignore [missing-import]
from flask import Blueprint, render_template, abort, request, send_file, redirect, url_for
# pyrefly: ignore [missing-import]
from flask_login import login_required, current_user
from app.utils.queries import (
    get_kpi_stats, get_occupancy_by_quarter, get_channel_distribution,
    get_guest_segment, get_hotel_revenue, get_room_type, get_nationality,
    get_recent_reservations, get_seasonal_trend, get_filter_options,
    get_okupansi_detail, get_customer_detail, get_room_detail, get_export_data
)
from app.models.user import User
from app import db
import json, io

admin = Blueprint('admin', __name__, url_prefix='/admin')

def get_filters():
    return (request.args.get('year'), request.args.get('hotel_type'), request.args.get('channel'))

def check_admin():
    if not current_user.is_admin():
        abort(403)

@admin.route('/dashboard')
@login_required
def dashboard():
    check_admin()
    year, hotel_type, channel = get_filters()
    return render_template('admin/dashboard.html',
        kpi         = get_kpi_stats(year, hotel_type, channel),
        occupancy   = get_occupancy_by_quarter(year, hotel_type, channel),
        channel     = get_channel_distribution(year, hotel_type, channel),
        segment     = get_guest_segment(year, hotel_type, channel),
        hotel_rev   = get_hotel_revenue(year, hotel_type, channel),
        room_type   = get_room_type(year, hotel_type, channel),
        nationality = get_nationality(year, hotel_type, channel),
        recent      = get_recent_reservations(10),
        seasonal    = get_seasonal_trend(year, hotel_type, channel),
        filter_opts = get_filter_options(),
        selected    = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )

@admin.route('/okupansi')
@login_required
def okupansi():
    check_admin()
    year, hotel_type, channel = get_filters()
    return render_template('admin/okupansi.html',
        data        = get_okupansi_detail(year, hotel_type, channel),
        occupancy   = json.dumps(get_occupancy_by_quarter(year, hotel_type, channel)),
        seasonal    = json.dumps(get_seasonal_trend(year, hotel_type, channel)),
        filter_opts = get_filter_options(),
        selected    = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )

@admin.route('/customer')
@login_required
def customer():
    check_admin()
    year, hotel_type, channel = get_filters()
    return render_template('admin/customer.html',
        data        = get_customer_detail(year, hotel_type, channel),
        segment     = json.dumps(get_guest_segment(year, hotel_type, channel)),
        nationality = json.dumps(get_nationality(year, hotel_type, channel)),
        filter_opts = get_filter_options(),
        selected    = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )

@admin.route('/room')
@login_required
def room():
    check_admin()
    year, hotel_type, channel = get_filters()
    return render_template('admin/room.html',
        data        = get_room_detail(year, hotel_type, channel),
        room_type   = json.dumps(get_room_type(year, hotel_type, channel)),
        filter_opts = get_filter_options(),
        selected    = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )

@admin.route('/export/<tipe>')
@login_required
def export(tipe):
    check_admin()
    year, hotel_type, channel = get_filters()
    fmt = request.args.get('format', 'excel')
    df  = get_export_data(tipe, year, hotel_type, channel)
    buf = io.BytesIO()
    if fmt == 'excel':
        df.to_excel(buf, index=False, engine='openpyxl')
        buf.seek(0)
        return send_file(buf, download_name=f'{tipe}_nusantara.xlsx',
                         as_attachment=True,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(buf, download_name=f'{tipe}_nusantara.csv',
                         as_attachment=True, mimetype='text/csv')

@admin.route('/kelola-user')
@login_required
def kelola_user():
    check_admin()
    users = User.query.all()
    return render_template('admin/kelola_user.html', users=users)

@admin.route('/kelola-user/tambah', methods=['POST'])
@login_required
def tambah_user():
    check_admin()
    username = request.form.get('username')
    email    = request.form.get('email')
    password = request.form.get('password')
    role     = request.form.get('role', 'user')
    if not User.query.filter_by(username=username).first():
        u = User(username=username, email=email, role=role)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
    return redirect(url_for('admin.kelola_user'))

@admin.route('/kelola-user/hapus/<int:uid>', methods=['POST'])
@login_required
def hapus_user(uid):
    check_admin()
    u = User.query.get_or_404(uid)
    if u.id != current_user.id:
        db.session.delete(u)
        db.session.commit()
    return redirect(url_for('admin.kelola_user'))
# pyrefly: ignore [missing-import]
from flask import jsonify

@admin.route('/db-status')
@login_required
def db_status():
    check_admin()
    from app.utils.queries import get_engine
    import pandas as pd
    engine = get_engine()
    try:
        stats = {}
        tables = ['fact_reservation', 'dim_guest', 'dim_hotel', 'dim_room', 'dim_time', 'dim_booking_channel']
        for t in tables:
            count = pd.read_sql(f"SELECT COUNT(*) AS n FROM {t}", engine).iloc[0]['n']
            stats[t] = int(count)
        cancelled = pd.read_sql("SELECT COUNT(*) AS n FROM fact_reservation WHERE is_cancelled='Yes'", engine).iloc[0]['n']
        active    = pd.read_sql("SELECT COUNT(*) AS n FROM fact_reservation WHERE is_cancelled='No'", engine).iloc[0]['n']
        return jsonify({
            'status': 'connected',
            'database': 'dw_hospitality',
            'tables': stats,
            'cancelled': int(cancelled),
            'active': int(active),
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    