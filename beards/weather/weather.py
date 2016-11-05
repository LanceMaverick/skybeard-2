import pyowm
import logging

def forecast(bot, update):
        owm = pyowm.OWM(config.api_key)
        message = update.message
        text = message.text
        
    
        forecast = owm.daily_forecast(location,limit=7)
        tomorrow = pyowm.timeutils.tomorrow()
        weather_tmrw = forecast.get_weather_at(tomorrow)
        
        true_location = forecast.get_forecast().get_location().get_name()
        coor_lon =  forecast.get_forecast().get_location().get_lon()
        coor_lat =  forecast.get_forecast().get_location().get_lat()
    
        lst_clouds = []
        lst_temp = []
        lst_status = []
        lst_time = []

        f_day = forecast.get_forecast()
        
        #get forecasts for each day
        for weather in f_day:
            lst_clouds.append( weather.get_clouds())
            lst_temp.append(weather.get_temperature('celsius')['max'])
            lst_status.append(weather.get_status())
            lst_time.append(weather.get_reference_time('iso'))

        temp_tomorrow = weather_tmrw.get_temperature('celsius')

        #check each status (quick implementation. Needs to be mapped)    
        if forecast.will_be_sunny_at(tomorrow):
            status = 'sunny'
        elif forecast.will_be_sunny_at(tomorrow):
            status = 'cloudy'
        elif forecast.will_be_rainy_at(tomorrow):
            status = 'rainy'
        elif forecast.will_be_snowy_at(tomorrow):
            status = 'snowy'
        elif forecast.will_be_stormy_at(tomorrow):
            status = 'stormy'
        elif forecast.will_be_foggy_at(tomorrow):
            status = 'foggy'
        elif forecast.will_be_tornado_at(tomorrow):
            status = 'TORNADO!!'
        elif forecast.will_be_hurricane_at(tomorrow):
            status = 'HURRICANE!!'
        else:
            status = '<unknown status>'
        
        fore_reply = 'At this time tomorrow in {}, it will be *{}* with a maximum temperature of *{}* degrees C'.format(
                true_location, status, str(temp_tomorrow['max']))

        #current weather observation   
        observation = owm.weather_at_place(location)
        weather = observation.get_weather()
        obs_wind = weather.get_wind()
        obs_temp = weather.get_temperature('celsius')
        
        obs_reply = 'Current weather status in *{}: {}*. \nWind speed (km/h):\t*{}*. Temperature (C)\t*{}*'.format(
                true_location, 
                str(weather.get_detailed_status()), 
                str(obs_wind['speed']),
                str(obs_temp['temp'])
                )
        
        message.reply_location(longitude= coor_lon, latitude = coor_lat)
        message.reply_text(obs_reply, parse_mode='Markdown')
        message.reply_text(fore_reply, parse_mode = 'markdown')
