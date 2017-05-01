from resources.lib.items import Items
import datetime
import ast
import resources.lib.simple_requests as requests
from resources.lib.bs4 import BeautifulSoup

items = Items()

ESLISTINGS_URL = "http://uk.eurosportplayer.com/tvschedule.xml"

def listings():
    #
    listings = getListing()
    #
    if listings:
        soup = BeautifulSoup(listings, 'html.parser')
        #
        li_all = soup.findAll("li", {"class": "tvschedule-main__right-program"})
        #
        proglist = {}
        #
        for li in li_all:
            #
            dateformat = '%Y-%m-%dT%H:%M:%S'
            dt_start = datetime.datetime.strptime(li.attrs['data-startdate'], dateformat)
            dt_end = datetime.datetime.strptime(li.attrs['data-enddate'], dateformat)
            #
            if dt_start >= datetime.datetime.now() or dt_end >= datetime.datetime.now():
                #
                if not 'no-prog' in li.attrs['class']:
                    #
                    data_prog = li.attrs['data-prg']
                    data_prog = ast.literal_eval(data_prog)
                    #
                    channel_id = data_prog['channelid']
                    title_full = data_prog['sporteventname']
                    title_short = data_prog['shortname']
                    desc = data_prog['description']
                    #

                    if data_prog['transmissiontype'] == '1':
                        live = ' [COLOR red]LIVE[/COLOR]'
                    else:
                        live = ''
                    #
                    dict_key = '{start_time}_{channel_id}'.format(start_time=dt_start.strftime('%Y-%m-%d_%H:%M'),
                                                                  channel_id=channel_id)
                    #
                    proglist[dict_key] = {'channel_id': channel_id,
                                          'title_full': title_full,
                                          'title_short': title_short,
                                          'desc': desc,
                                          'live': live,
                                          'dt_start': dt_start,
                                          'dt_end': dt_end}
                    #
        for key in sorted(proglist.iterkeys()):
            #
            item_label = '{time}{live} {title}'.format(time=proglist[key]['dt_start'].strftime("%d-%m-%Y %H:%M"),
                                                       live=proglist[key]['live'],
                                                       title=proglist[key]['title_full'])
            #
            items.add({'mode': '#', 'title': item_label})
    #
    items.list()

def getListing():
    #
    r = requests.get(ESLISTINGS_URL)
    #
    if r.status_code == 200:
        return r.text
    else:
        return False