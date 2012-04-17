#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from urllib import quote

from grab import Grab
from grab.spider import Spider, Task

from elixir import session

import model


additional_headers = {
         'Accept-Charset': 'utf-8',
         'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'
    }


class ShoutCastCom(Spider):
    def prepare(self):
        self.grab = Grab()
        self.grab.setup(headers=additional_headers)

    def get_grab(self, url=None):
        grab = self.grab.clone()
        if url:
            grab.setup(url=url)
        return grab

    def get_task(self, **kwargs):
        grab = self.grab.clone()

        if 'grab' in kwargs:
            grab.setup(**kwargs['grab'])
            del kwargs['grab']

        return Task(
                grab=grab,
                **kwargs
            )

    def get_kwargs(self, **kwargs):
        return kwargs

    def task_generator(self):
        self.grab_genres()

        for genre in model.Genre.query.all():
            yield self.get_next_stations(genre)

        raise StopIteration

    def get_next_stations(self, genre, last=0):
        url = 'http://www.shoutcast.com/genre-ajax/%s' % (quote(genre.name))
        grab_options = self.get_kwargs(
                post={
                        'strIndex': last,
                        'count': 10,
                        #'ajax': 'true',
                        #'mode': 'listeners',
                        #'order': 'desc',
                    },
                log_dir='/tmp/shout/',
                url=url
            )

        return self.get_task(
                name='stations',
                genre=genre,
                last=last + 10,
                grab=grab_options
            )

    def task_stations(self, grab, task):
        if grab.xpath_exists('//span[contains(text(), "show more")]'):
            yield self.get_next_stations(
                    task.genre,
                    task.last
                )

        for dirlist in grab.xpath_list('//div[@class="dirlist"]'):
            info = dirlist.xpath('./div[1]/a[1]')[0]
            url, name = info.get('href'), info.get('name')

            stream = dirlist.xpath('./div[@class="dirtype"]/text()')[0]
            bitrate = dirlist.xpath('./div[@class="dirbitrate"]/text()')[0]

            '''print '  %s[%s] - %s [%s]' % (
                    stream,
                    bitrate,
                    name,
                    url
                )'''

            self.get_station(
                    name,
                    url,
                    stream,
                    bitrate,
                    task.genre
                )

        session.commit()

    def get_genre(self, name, url, parent=None):
        return model.get_or_create(
                model.Genre,
                name=name,
                url=url,
                parent=parent
            )

    def get_station(self, name, url, stream, bitrate, genre):
        stream = model.get_or_create(
                model.Stream,
                name=stream
            )
        return model.get_or_create(
                model.Station,
                name=name,
                url=url,
                stream=stream,
                bitrate=bitrate,
                genre=genre,
            )

    def grab_genres(self):
        grab = self.get_grab('http://www.shoutcast.com/')
        grab.request()

        grab.setup(url='http://www.shoutcast.com/genre.jsp')

        for genre in grab.xpath_list('//li[@class="prigen"]/a'):
            genre = self.get_genre(
                    name=genre.xpath('./text()')[0],
                    url=genre.get('href')
                )

            grab.setup(
                    post={
                            'genre': genre.name
                        }
                )
            grab.request()

            for subgenre in grab.xpath_list('//li[@class="secgen"]/a'):
                subgenre = self.get_genre(
                        name=subgenre.xpath('./text()')[0],
                        url=subgenre.get('href'),
                        parent=genre
                    )

        session.commit()


if __name__ == '__main__':
    print model.Genre.query.count()
    print model.Stream.query.count()
    print model.Station.query.count()

    parser = ShoutCastCom(thread_number=1)
    parser.run()

    sys.exit()
