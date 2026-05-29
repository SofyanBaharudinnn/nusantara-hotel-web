from flask import Blueprint, render_template, request
from flask_login import login_required
from app.utils.queries import (
    get_kpi_stats, get_seasonal_trend, get_guest_segment,
    get_nationality, get_room_type, get_occupancy_by_quarter,
    get_filter_options, get_channel_distribution,
    get_okupansi_detail, get_customer_detail, get_room_detail
)
import json

user = Blueprint('user', __name__, url_prefix='/user')

def get_filters():
    return (request.args.get('year'), request.args.get('hotel_type'), request.args.get('channel'))

@user.route('/dashboard')
@login_required
def dashboard():
    year, hotel_type, channel = get_filters()
    return render_template('user/dashboard.html',
        kpi          = get_kpi_stats(year, hotel_type, channel),
        seasonal     = json.dumps(get_seasonal_trend(year, hotel_type, channel)),
        segment      = json.dumps(get_guest_segment(year, hotel_type, channel)),
        nationality  = json.dumps(get_nationality(year, hotel_type, channel)),
        room_type    = json.dumps(get_room_type(year, hotel_type, channel)),
        occupancy    = json.dumps(get_occupancy_by_quarter(year, hotel_type, channel)),
        channel_data = json.dumps(get_channel_distribution(year, hotel_type, channel)),
        filter_opts  = get_filter_options(),
        selected     = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )

@user.route('/okupansi')
@login_required
def okupansi():
    year, hotel_type, channel = get_filters()
    return render_template('user/okupansi.html',
        data        = get_okupansi_detail(year, hotel_type, channel),
        occupancy   = json.dumps(get_occupancy_by_quarter(year, hotel_type, channel)),
        seasonal    = json.dumps(get_seasonal_trend(year, hotel_type, channel)),
        filter_opts = get_filter_options(),
        selected    = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )

@user.route('/customer')
@login_required
def customer():
    year, hotel_type, channel = get_filters()
    return render_template('user/customer.html',
        data        = get_customer_detail(year, hotel_type, channel),
        segment     = json.dumps(get_guest_segment(year, hotel_type, channel)),
        nationality = json.dumps(get_nationality(year, hotel_type, channel)),
        filter_opts = get_filter_options(),
        selected    = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )

@user.route('/seasonal')
@login_required
def seasonal():
    year, hotel_type, channel = get_filters()
    return render_template('user/seasonal.html',
        seasonal    = json.dumps(get_seasonal_trend(year, hotel_type, channel)),
        occupancy   = json.dumps(get_occupancy_by_quarter(year, hotel_type, channel)),
        kpi         = get_kpi_stats(year, hotel_type, channel),
        filter_opts = get_filter_options(),
        selected    = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )

@user.route('/room')
@login_required
def room():
    year, hotel_type, channel = get_filters()
    return render_template('user/room.html',
        data        = get_room_detail(year, hotel_type, channel),
        room_type   = json.dumps(get_room_type(year, hotel_type, channel)),
        filter_opts = get_filter_options(),
        selected    = {'year': year, 'hotel_type': hotel_type, 'channel': channel},
    )