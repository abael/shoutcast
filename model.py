#! /usr/bin/env python
# -*- coding: utf-8 -*-

from elixir import Entity, Field, String, ManyToOne, DateTime, Integer, metadata, create_all, setup_all


class Genre(Entity):
    url = Field(String(256))
    name = Field(String(256))
    parent = ManyToOne('Genre')

    def __init__(self, **kwars):
        for key, value in kwars.items():
            setattr(self, key, value)

    def __repr__(self):
        parent = [self.parent.name] if self.parent else []
        return '<Genre %s>' % (' / '.join(parent + [self.name]))


class Stream(Entity):
    name = Field(String(15))

    def __init__(self, **kwars):
        for key, value in kwars.items():
            setattr(self, key, value)


class Station(Entity):
    url = Field(String(256))
    name = Field(String(256))
    date = Field(DateTime)

    bitrate = Field(Integer)
    stream = ManyToOne('Stream')

    genre = ManyToOne('Genre')

    def __init__(self, **kwars):
        for key, value in kwars.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Station %s>' % (self.name)


def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        return model(**kwargs)


metadata.bind = 'sqlite:///shoutcast.com.db'
metadata.bind.echo = False

#create_all()
setup_all(create_tables=True)
