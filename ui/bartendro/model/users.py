# -*- coding: utf-8 -*-
from bartendro import db
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, Column, Integer, String, MetaData, Unicode, UnicodeText, UniqueConstraint, Text, Index
from sqlalchemy.ext.declarative import declarative_base

class Users(db.Model):
    """
    Information about a users 
    """

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(UnicodeText, nullable=False)
    password = Column(UnicodeText, nullable=True)
    credit = Column(Integer, default=0)
    administrator = Column(Integer, default=0)
    superadministrator = Column(Integer, default=0)

    # add unique constraint for name
    UniqueConstraint('username', name='users_username_undx')
 
    query = db.session.query_property()
    def __init__(self, username = u'', password = u'', credit = 0, administrator = 0, superadministrator = 0, out = 0, data = None):
        if data: 
            self.update(data)
            return
        self.username = username
        self.password = password
        self.credit = credit
        self.administrator = administrator
        self.superadministrator = superadministrator
        self.out = out

    def update(self, data):
        self.username = data['username']
        self.password = data['password']
        self.credit = int(data['credit'])
        self.administrator = int(data['administrator'])
        self.superadministrator = int(data['superadministrator'])

    def __repr__(self):
        return "<User('%s','%s')>" % (self.id, self.username)

Index('users_username_ndx', Users.username)
