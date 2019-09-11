import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from database import db_session, User as UserModel, Device as DeviceModel


class Device(SQLAlchemyObjectType):
    class Meta:
        model = DeviceModel
        interfaces = (relay.Node, )


class DeviceConnection(relay.Connection):
    class Meta:
        node = Device


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )


class UserConnection(relay.Connection):
    class Meta:
        node = User


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_users = SQLAlchemyConnectionField(User._meta.connection)
    all_devices = SQLAlchemyConnectionField(Device._meta.connection)
    users = SQLAlchemyConnectionField(User)


class CreateUser(graphene.Mutation):
    class Input:
        name = graphene.String()
        age = graphene.Int()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    @classmethod
    def mutate(cls, root, info, **args):
        user = UserModel(name=args.get('name'), age=args.get('age'))
        db_session.add(user)
        db_session.commit()
        ok = True
        return CreateUser(user=user, ok=ok)


class MyMutations(graphene.ObjectType):
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=MyMutations)
