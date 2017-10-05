from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database_setup import Category , Items ,Base,User

engine = create_engine('sqlite:///ItemCatalogwithUser.db')

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

User1 = User(name="Apexa patel", email="apexakpatel7@gmail.com",
             picture='https://pbs.twimg.com/profile_images/711124059564548096/796W67Sb_400x400.jpg')
session.add(User1)
session.commit()


category1 = Category(name = 'Women' ,user_id = 1)
category2 = Category(name = 'Men', user_id = 1)
category3 = Category(name = 'Baby', user_id = 1)
category4 = Category(name = 'Books', user_id = 1)

session.add(category1)
session.add(category2)
session.add(category3)
session.add(category4)
session.commit()

items1 = Items(user_id = 1,name = 'Clothing' ,description = 'Stylist Dress', img_url ="https://ae01.alicdn.com/kf/HTB1IdHhLFXXXXaoXFXXq6xXFXXXD/Navy-Blue-Oversized-Long-Sleeve-Women-Clothing-Home-House-Dress-With-Belt-Summer-Long-Shirt-Dress.jpg", category = category1)
items2 = Items(user_id = 1,name = 'Watches' , description = 'Luxury watches' ,img_url="https://slimages.macysassets.com/is/image/MCY/products/5/optimized/8310605_fpx.tif?bgc=255,255,255&wid=224&qlt=90,0&layer=comp&op_sharpen=0&resMode=bicub&op_usm=0.7,1.0,0.5,0&fmt=jpeg" ,category = category1)
items3 = Items(user_id = 1,name = 'shoes', description = 'high heels' ,img_url="http://images6.fanpop.com/image/photos/33300000/i-love-it-womens-shoes-33329749-500-500.jpg" ,category = category1)
session.add(items1)
session.add(items2)
session.add(items3)
session.commit()

items4 = Items(user_id = 1,name = 'Clothing' ,description = 'casual shirts',img_url="https://s-media-cache-ak0.pinimg.com/originals/f6/e9/b2/f6e9b2eb3f3e896b4ab605f19b901c8e.jpg" ,category = category2)
items5 = Items(user_id = 1,name = 'watches' , description = 'Luxury watches' ,img_url="https://ae01.alicdn.com/kf/HTB1GylxKpXXXXa5XpXXq6xXFXXXr/YAZOLE-Leather-Watches-Men-Luxury-Brand-Waterproof-Analog-Stainless-Steel-Business-Quartz-Watch-Casual-Man-relogios.jpg_640x640.jpg" ,category = category2)
items6 = Items(user_id = 1,name = 'Shoes', description = 'casual shoes' ,img_url="http://www.business-casualforwomen.com/wp-content/uploads/2015/11/business-casual-shoes-men-best-outfits-3.jpg" ,category = category2)
session.add(items4)
session.add(items5)
session.add(items6)
session.commit()

items7 = Items(user_id = 1,name = 'Clothing' ,description = 'dress',img_url="http://clothing.beautysay.net/wp-content/uploads/images/trendy-baby-girl-clothes-2.jpg" ,category = category3)
items8 = Items(user_id = 1,name = 'shoes' , description = 'Shoes' ,img_url="http://roud.jlong.wang/Y%20T/YTM1125/YTM1125P%20%281%29.jpg" ,category = category3)

session.add(items7)
session.add(items8)
session.commit()

items10 = Items(user_id = 1,name = 'Love story' ,description = 'beautiful Love story',img_url="https://images-na.ssl-images-amazon.com/images/I/71JJMJzDHLL.jpg" ,category = category4)
items11 = Items(user_id = 1,name = 'motivation story' , description = 'story about life,hardwork and goals', img_url="https://qph.ec.quoracdn.net/main-qimg-97dca59131639d906ddfd6ba5de0565d" ,category = category4)
items12 = Items(user_id = 1,name = 'fairy tale story', description = 'beautiful fairy tale love story' ,img_url="https://i2.wp.com/www.my-sf.com/wp-content/uploads/2013/08/Tinker-Bell-and-the-Great-Fairy-Rescue-poster-UK.jpg" ,category = category4)
session.add(items10)
session.add(items11)
session.add(items12)
session.commit()


print "add all items in catalog"

