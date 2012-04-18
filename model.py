#! /usr/bin/env python
# -*- coding: utf-8 -*-

from elixir import (metadata, Entity, ManyToOne, ManyToMany,
                    Field, String,
                    create_all, setup_all, drop_all)


class Genre(Entity):
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

    def __repr__(self):
        return '<%s>' % (self.name)


class Bitrate(Entity):
    name = Field(String(8))

    def __init__(self, **kwars):
        for key, value in kwars.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<%s>' % (self.name)


class Station(Entity):
    name = Field(String(256))
    url = Field(String(256))

    bitrate = ManyToOne('Bitrate')
    stream = ManyToOne('Stream')

    genres = ManyToMany('Genre')

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


metadata.bind = 'mysql://root:654321@localhost/shoutcast'
metadata.bind.echo = False

create_all()
setup_all()
