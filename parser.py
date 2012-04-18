#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from urllib import quote
from optparse import OptionParser

from grab import Grab
from grab.spider import Spider, Task

from elixir import session

import model


additional_headers = {
     'Accept-Charset': 'utf-8',
     'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'
}


class ShoutCastCom(Spider):
    def __init__(self, *kargs, **kwargs):
        super(ShoutCastCom, self).__init__(*kargs, **kwargs)
        self.setup_grab(headers=additional_headers)

    def task_generator(self):
        yield Task(name='genres',
                   url='http://www.shoutcast.com/')

    def task_genres(self, grab, task):
        genres = grab.xpath_list('//li[@class="prigen"]/a/text()')

        for genre in genres:
            genre_record = model.get_or_create(model.Genre,
                                               name=genre,
                                               parent=None)

            grab = self.create_grab_instance()
            grab.setup(url='http://www.shoutcast.com/genre.jsp',
                       post=dict(genre=genre))

            yield Task(name='subgenres',
                       genre=genre_record,
                       grab=grab)

            yield self.new_stations_task(genre=genre_record,
                                         start_index=0)

    def task_subgenres(self, grab, task):
        subgenres = grab.xpath_list('//li[@class="secgen"]/a/text()')

        for subgenre in subgenres:
            subgenre_record = model.get_or_create(model.Genre,
                                                  name=subgenre,
                                                  parent=task.genre)

            yield self.new_stations_task(genre=subgenre_record,
                                         start_index=0)

    def new_stations_task(self, genre, start_index, count=100):
        url = 'http://www.shoutcast.com/genre-ajax/%s' % (quote(genre.name))

        grab = self.create_grab_instance()
        grab.setup(url=url,
                   post=dict(strIndex=start_index, count=count))

        return Task(name='stations',
                    genre=genre,
                    grab=grab,
                    last=start_index)

    def task_stations(self, grab, task):
        stations = grab.xpath_list('//div[@class="dirlist"]')

        if grab.xpath_exists('//span[contains(text(), "show more")]'):
            yield self.new_stations_task(genre=task.genre,
                                         start_index=task.last + len(stations))

        for dirlist in stations:
            info = dirlist.xpath('./div[1]/a[1]')[0]
            url, name = info.get('href'), info.get('name')

            stream = dirlist.xpath('./div[@class="dirtype"]/text()')[0]
            bitrate = dirlist.xpath('./div[@class="dirbitrate"]/text()')[0]

            stream = model.get_or_create(model.Stream,
                                         name=stream)

            bitrate = model.get_or_create(model.Bitrate,
                                          name=bitrate)

            station = model.get_or_create(model.Station,
                                          name=name,
                                          url=url,
                                          stream=stream,
                                          bitrate=bitrate)

            station.genres.append(task.genre)

        if stations:
            session.commit()


def main():
    parser = OptionParser(description=u'Парсер радиостанций www.ShoutCast.com')

    parser.add_option('-t',
                      action="store",
                      dest='threads_count',
                      default=10,
                      help=u'количество потоков')

    options, _ = parser.parse_args()

    parser = ShoutCastCom(thread_number=options.threads_count)
    parser.run()

    sys.exit()


if __name__ == '__main__':
    main()
