from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database_setup import Category , Items ,Base

engine = create_engine('sqlite:///catalog.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


category1 = Category(name = 'Women')
category2 = Category(name = 'Men')
category3 = Category(name = 'Baby')
category4 = Category(name = 'Beauty')
category5 = Category(name = 'Electronic')
category6 = Category(name = 'Bags')
category7 = Category(name = 'Shoes')
category8 = Category(name = 'Toys')
category9 = Category(name = 'Stationary')
category10 = Category(name = 'food')

session.add(category1)
session.add(category2)
session.add(category3)
session.add(category4)
session.add(category5)
session.add(category6)
session.add(category7)
session.add(category8)
session.add(category9)
session.add(category10)
session.commit()

items1 = Items(name = 'dress' ,description = 'long dress', category = category1)
items2 = Items(name = 'top' , description = 'summer - top' , category = category1)
items3 = Items(name = 'pant', description = 'cotton pants' , category = category1)
session.add(items1)
session.add(items2)
session.add(items3)
session.commit()

items4 = Items(name = 'shirt' ,description = 'cotton shirts', category = category2)
items5 = Items(name = 'tees' , description = 'summer - tees' , category = category2)
items6 = Items(name = 'pant', description = 'cotton pants' , category = category2)
session.add(items4)
session.add(items5)
session.add(items6)
session.commit()

items7 = Items(name = 'dress' ,description = 'long dress', category = category3)
items8 = Items(name = 'top' , description = 'summer - top' , category = category3)
items9 = Items(name = 'pant', description = 'cotton pants' , category = category3)
session.add(items7)
session.add(items8)
session.add(items9)
session.commit()

items10 = Items(name = 'eye-shadow' ,description = 'mac eye-shadow', category = category4)
items11 = Items(name = 'lipstick' , description = 'mac lipstick'  ,category = category4)
items12 = Items(name = 'blush', description = 'mac blush' , category = category4)
session.add(items10)
session.add(items11)
session.add(items12)
session.commit()

items13 = Items(name = 'iron' ,description = 'bajaj - iron', category = category5)
items14 = Items(name = 'lamp' , description = 'bajaj- lamp' ,category = category5)
items15 = Items(name = 'fan', description = 'bajaj- fan' , category = category5)
session.add(items13)
session.add(items14)
session.add(items15)
session.commit()

items16 = Items(name = 'tote' ,description = 'lavie tote', category = category6)
items17 = Items(name = 'sling bag' , description = 'coach swing bag' ,category= category6)
items18 = Items(name = 'handbag', description = 'lino handbag' , category = category6)
session.add(items16)
session.add(items17)
session.add(items18)
session.commit()

items19 = Items(name = 'sports shoes' ,description = 'running,football,gym shoes', category = category7)
items20 = Items(name = 'formal shoes' , description = 'office shoes'  ,category = category7)
items21 = Items(name = 'sandal', description = 'lino sandal' , category = category7)
session.add(items18)
session.add(items19)
session.add(items20)
session.commit()

items22 = Items(name = 'indoor toys' ,description = 'doll,gun', category = category8)
items23 = Items(name = 'outdoor toys' , description = 'sketting, toycar'  ,category = category8)
items24 = Items(name = 'bicycle', description = 'toy bicycle' , category = category8)
session.add(items22)
session.add(items23)
session.add(items24)
session.commit()

items25 = Items(name = 'papers' ,description = 'notebook,fullscapebook', category = category9)
items26 = Items(name = 'office supplies' , description = 'stapler,folders'  ,category = category9)
items27 = Items(name = 'studen stuff', description = 'caculator,file' , category = category9)
session.add(items25)
session.add(items26)
session.add(items27)
session.commit()

items28 = Items(name = 'waffers' ,description = 'potato waffers', category = category10)
items29 = Items(name = 'chocolates' , description = 'dark chocolates' ,category = category10)
items30 = Items(name = 'pizza', description = 'veg. pizza with selected veggies' , category = category10)
session.add(items28)
session.add(items29)
session.add(items30)
session.commit()

print "add all items in catalog"

