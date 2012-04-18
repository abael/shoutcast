#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import model


if __name__ == '__main__':
    print u'Жанров: %d' % (model.Genre.query.count())
    print u'Битрейтов: %d' % (model.Bitrate.query.count())
    print u'Потоков: %d' % (model.Stream.query.count())
    print u'Радиостанций: %d' % (model.Station.query.count())

    total = 0
    for station in model.Station.query.all():
        total += len(station.genres)

    print u'с учетом жанров: %d' % (total)

    sys.exit()
