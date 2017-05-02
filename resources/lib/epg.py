from resources.lib.items import Items
import time, datetime
import ast
from resources.lib.common import *
import resources.lib.simple_requests as requests
from resources.lib.bs4 import BeautifulSoup

items = Items()

ESLISTINGS_URL = "http://uk.eurosportplayer.com/tvschedule.xml"
ESLISTINGS_dt_format = '%Y-%m-%dT%H:%M:%S'

def listings():
    #
    try:
        #
        listings = getListing()
        #
        if listings:
            soup = BeautifulSoup(listings, 'html.parser')
            #
            li_all = soup.findAll("li", {"class": "tvschedule-main__right-program"})
            #
            if len(li_all) == 0:
                raise Exception('No <li> tags with class = "tvschedule-main__right-program" received')
            #
            proglist = {}
            #
            for li in li_all:
                #
                try:
                    #
                    if not 'no-prog' in li.attrs['class']:
                        #
                        s = li.attrs['data-startdate']
                        try:
                            dt_start = datetime.datetime.strptime(s, ESLISTINGS_dt_format)
                        except TypeError:
                            dt_start = datetime.datetime(*(time.strptime(s, ESLISTINGS_dt_format)[0:6]))
                        #
                        e = li.attrs['data-enddate']
                        try:
                            dt_end = datetime.datetime.strptime(e, ESLISTINGS_dt_format)
                        except TypeError:
                            dt_end = datetime.datetime(*(time.strptime(e, ESLISTINGS_dt_format)[0:6]))
                        #
                        ################################################################
                        # NOTE: Below two lines are simplified versions of the above code,
                        # however due to known bug with python they do not work:
                        # http://bugs.python.org/issue27400
                        #
                        # dt_start = datetime.datetime.strptime(s, ESLISTINGS_dt_format)
                        # dt_end = datetime.datetime.strptime(e, ESLISTINGS_dt_format)
                        #################################################################
                        #
                        if dt_start >= datetime.datetime.now() or dt_end >= datetime.datetime.now():
                            #
                            data_prog = ast.literal_eval(li.attrs['data-prg'])
                            #
                            channel_id = data_prog.get('channelid', '')
                            title_full = data_prog.get('sporteventname', '')
                            title_short = data_prog.get('shortname', '')
                            desc = data_prog.get('description', '')
                            img = data_prog.get('data-channelimg', '')
                            #
                            log('** Position 05 **')
                            if data_prog.get('transmissiontype', '') == '1':
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
                                                  'img': img,
                                                  'dt_start': dt_start,
                                                  'dt_end': dt_end}
                except Exception as e:
                    log('Eurosportplayer: ERROR attempting to gather information from <li> item - {error}'.format(error=e))
            #
            for key in sorted(proglist.iterkeys()):
                #
                try:
                    if proglist[key]['dt_start'] <= datetime.datetime.now() <= proglist[key]['dt_end']:
                        datetime_lbl = 'NOW'
                    else:
                        if proglist[key]['dt_start'].strftime("%d-%m-%Y") == datetime.datetime.now().strftime("%d-%m-%Y"):
                            start_date = 'Today'
                        elif proglist[key]['dt_start'].strftime("%d-%m-%Y") == (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y"):
                            start_date = 'Tomorrow'
                        else:
                            start_date = proglist[key]['dt_start'].strftime("%d-%m"),
                        #
                        datetime_lbl = '{start_date} {start_time}'.format(start_date=start_date,
                                                                          start_time=proglist[key]['dt_start'].strftime("%H:%M"))
                    #
                    duration = int((proglist[key]['dt_end'] - proglist[key]['dt_start']).total_seconds() // 60)
                    #
                    item_label = '{datetime_lbl}{live} [I]{title}[/I]  [{duration} mins]'.format(datetime_lbl=datetime_lbl,
                                                                                                 live=proglist[key]['live'],
                                                                                                 title=proglist[key]['title_full'],
                                                                                                 duration=str(duration))
                    #
                    items.add({'mode': '#', 'title': item_label, 'thumb': proglist[key]['img']})
                    #
                except Exception as e:
                    log('Eurosportplayer: ERROR attempting to build xbmc list item for {prog} - {error}'.format(prog=proglist[key]['title_full'],
                                                                                                                error=e))
        #
        items.list()
        #
    except Exception as e:
        log('Eurosportplayer: ERROR attempting to retrieve and present tv schedule - {error}'.format(error=e))

def getListing():
    #
    r = requests.get(ESLISTINGS_URL)
    #
    if r.status_code == 200:
        return r.text
    else:
        log('Eurosportplayer: ERROR attempting to retrieve - status code {code} returned'.format(code=r.status_code))
        return False