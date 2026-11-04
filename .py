from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///rental.db")
Session = sessionmaker(bind=engine)
session = Session()


class Client(Base):
    __tablename__ = "client"
    id   = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)

class Employee(Base):
    __tablename__ = "employee"
    id   = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Type(Base):
    __tablename__ = "equipment_type"
    id    = Column(Integer, primary_key=True)
    name  = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)

class Item(Base):
    __tablename__ = "equipment_item"
    id     = Column(Integer, primary_key=True)
    number = Column(String, unique=True, nullable=False)
    type_id = Column(Integer, ForeignKey("equipment_type.id"), nullable=False)
    status = Column(String, default="available")

class Contract(Base):
    __tablename__ = "rental_contract"
    id         = Column(Integer, primary_key=True)
    client_id  = Column(Integer, ForeignKey("client.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)

class RentItem(Base):
    __tablename__ = "rental_item"
    id          = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("rental_contract.id"), nullable=False)
    item_id     = Column(Integer, ForeignKey("equipment_item.id"), nullable=False)
    price       = Column(Integer, nullable=False)  # цена на момент выдачи
    returned    = Column(Integer, default=0)       # 0/1

class Payment(Base):
    __tablename__ = "payment"
    id          = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("rental_contract.id"), nullable=False)
    amount      = Column(Integer, nullable=False)

Base.metadata.create_all(engine)



session.add_all([
    Client(name="Иванов", phone="+79001112233"),
    Client(name="Петрова", phone="+79004445566"),
    Employee(name="Смирнов"),
    Employee(name="Кузнецова"),
    Type(name="велосипед", price=500),
    Type(name="самокат",   price=300),
    Type(name="лыжи",      price=700),
])
session.commit()

session.add_all([
    Item(number="BIKE-001",  type_id=1, status="available"),
    Item(number="BIKE-002",  type_id=1, status="available"),
    Item(number="SCOOT-001", type_id=2, status="available"),
    Item(number="SKI-001",   type_id=3, status="maintenance"),
    Item(number="SCOOT-002", type_id=2, status="rented"),
    Contract(client_id=1, employee_id=1),
    Contract(client_id=2, employee_id=1),
])
session.commit()

session.add_all([
    RentItem(contract_id=1, item_id=1, price=500),
    RentItem(contract_id=1, item_id=3, price=300),
    RentItem(contract_id=2, item_id=5, price=300),
    Payment(contract_id=1, amount=500),
    Payment(contract_id=2, amount=100),
])
session.commit()


print("Доступные велосипеды:")
for i in session.query(Item).join(Type).filter(Type.name == "велосипед",
                                               Item.status == "available"):
    print(" ", i.number)


print("Невозвращённые:")
for r in session.query(RentItem, Client).join(Contract).join(Client):
    if r.RentItem.returned == 0:
        print(" ", r.Client.name, r.RentItem.item_id)


print("Долги:")
for c in session.query(Contract):
    charged = sum(x.price for x in c.id and
                  session.query(RentItem).filter_by(contract_id=c.id))
    paid = sum(p.amount for p in session.query(Payment).filter_by(contract_id=c.id))
    print(f"  договор {c.id}: долг {charged - paid}")


print("Выдачи по видам:")
for t in session.query(Type):
    cnt = (session.query(RentItem).join(Item, RentItem.item_id == Item.id)
           .filter(Item.type_id == t.id).count())
    print(f"  {t.name}: {cnt}")

session.close()
