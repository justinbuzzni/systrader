from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///report.db')
Base = declarative_base()


def get_session():
    return sessionmaker(bind=engine)()


class Buy(Base):
    __tablename__ = 'buy'
    id = Column(Integer, primary_key=True)
    dt = Column(String(), nullable=False)
    code = Column(String(), nullable=False)
    name = Column(String(), nullable=False)
    price = Column(Integer(), nullable=False)
    amount = Column(Integer(), nullable=False)
    features = Column(String(), nullable=True)

    def __repr__(self):
        return "[Buy][{dt}] {name}({code}): {price} {amount}".format(
            dt=self.dt, name=self.name, code=self.code, price=self.price, amount=self.amount
        )


class Sell(Base):
    __tablename__ = 'sell'
    id = Column(Integer, primary_key=True)
    dt = Column(String(), nullable=False)
    code = Column(String(), nullable=False)
    name = Column(String(), nullable=False)
    price = Column(Integer(), nullable=False)
    amount = Column(Integer(), nullable=False)
    decision = Column(String(), nullable=False)
    features = Column(String(), nullable=True)

    def __repr__(self):
        return "[Sell][{dt}] {name}({code}): {price} {amount} {decision}".format(
            dt=self.dt, name=self.name, code=self.code, price=self.price, amount=self.amount,
            decision=self.decision
        )


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = get_session()
    session.add(Buy(dt='20170803093010', code='000000', name='A', price=1000, amount=10))
    session.commit()
    print(session.query(Buy).first())