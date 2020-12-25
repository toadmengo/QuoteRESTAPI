from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import random
import datetime
import json

password = 'quoteapp'
getkey = 'get'

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_BINDS'] = {'two': 'sqlite:///usermodel.db'}

db = SQLAlchemy(app)


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(300), nullable = False)
    author = db.Column(db.String(100), nullable = False)
    likes = db.Column(db.Integer, nullable = False)
    religious = db.Column(db.Boolean, nullable = True)
    science = db.Column(db.Boolean, nullable = True)


class UserModel(db.Model):
    __bind_key__ = 'two'
    id = db.Column(db.Integer, primary_key = True)
    firstQuoteID = db.Column(db.Integer)
    secondQuoteID = db.Column(db.Integer)
    thirdQuoteID = db.Column(db.Integer)

#db.create_all()

quotes_put_args = reqparse.RequestParser()
quotes_put_args.add_argument("content", type = str, help = "Quote content", required = True)
quotes_put_args.add_argument("author", type = str, help = "Quote author", required = True)
quotes_put_args.add_argument("likes", type = int, help = "Quote likes", required = True)
quotes_put_args.add_argument("religious", type = bool, help = "relgious quote?", required = False)
quotes_put_args.add_argument("science", type = bool, help = "science quote?", required = False)

quotes_patch_args = reqparse.RequestParser()
quotes_patch_args.add_argument("content", type = str, help = "Quote content")
quotes_patch_args.add_argument("author", type = str, help = "Quote author")
quotes_patch_args.add_argument("likes", type = int, help = "Quote likes")
quotes_patch_args.add_argument("religious", type = bool, help = "relgious quote?")
quotes_patch_args.add_argument("science", type = bool, help = "science quote?")

resource_fields = {
    'id': fields.Integer,
    'content': fields.String,
    'author': fields.String,
    'likes': fields.Integer,
    'religious': fields.Boolean,
    'science': fields.Boolean
}

resource_fields_userID = {
    'id': fields.Integer
}

class Quotes(Resource):
    @marshal_with(resource_fields)
    def get(self, quote_id, key):
        if key == getkey:
            result = QuoteModel.query.filter_by(id = quote_id).first()
            return result
        else:
            return "incorrect key"
    
    @marshal_with(resource_fields)
    def post(self, quote_id, key):
        args = quotes_put_args.parse_args()
        result = QuoteModel.query.filter_by(id = quote_id).first()
        print(args)
        if result:
            abort(400, message = 'id taken')
        if key == password:
            quote = QuoteModel(id=quote_id, content = args['content'], author = args['author'], likes = args['likes'], religious = args['religious'], science = args['science'])
            db.session.add(quote)
            db.session.commit()
            return quote, 201
        else:
            return "incorrect key", 200

    @marshal_with(resource_fields)
    def put(self, quote_id, key):
        if key == 'update':
            args = quotes_patch_args.parse_args()
            result = QuoteModel.query.filter_by(id = quote_id).first()
            if not result:
                print('error')
                abort(404, message='DNE')
            if args['likes']:
                totalLikes = result.likes
                result.likes = args['likes'] + totalLikes
            db.session.commit()
            return
        return


    @marshal_with(resource_fields)
    def delete(self, quote_id, key):
        if key == password:
            result = QuoteModel.query.filter_by(id = quote_id).first()
            if result:
                db.session.delete(result)
                db.session.commit()
                return "", 204
            else:
                abort(400, message = 'id not found')
        else:
            return "incorrect key", 200


api.add_resource(Quotes, "/quotes/<int:quote_id>/<string:key>")

class UserData(Resource):

    @marshal_with(resource_fields_userID)
    def post(self, userID, currentTime, setTime):
        if userID == 0:
            usercount = UserModel.query.count()
            newUserID = usercount + 1

            count = QuoteModel.query.count()
            randomIDs = random.sample(range(1, count), 3)

            newUser = UserModel(id = newUserID, firstQuoteID = randomIDs[0], secondQuoteID = randomIDs[1], thirdQuoteID = randomIDs[2])
            db.session.add(newUser)
            db.session.commit()
            
            userID = newUserID

        idDict = {"id": userID}
        print(idDict)
        jsonObj = json.dumps(idDict)
        return idDict

    @marshal_with(resource_fields)
    def get(self, userID, currentTime, setTime):
        setTimeComponents = setTime.split("T")
        setTimeDate = setTimeComponents[0].split("-")
        setTimeTime = setTimeComponents[1].split(":")
        setTime = datetime.datetime(int(setTimeDate[0]), int(setTimeDate[1]), int(setTimeDate[2]), int(setTimeTime[0]), 0)
        currentTimeComponents = currentTime.split("T")
        currentTimeDate = currentTimeComponents[0].split("-")
        currentTimeTime = currentTimeComponents[1].split(":")
        currentTime = datetime.datetime(int(currentTimeDate[0]), int(currentTimeDate[1]), int(currentTimeDate[2]), int(currentTimeTime[0]), 0)
        print(setTime, currentTime)
        if currentTime >= setTime + datetime.timedelta(days=1):
            count = QuoteModel.query.count()
            randomIDs = random.sample(range(1, count), 3)
            result = UserModel.query.filter_by(id = userID).first()
            result.firstQuoteID = randomIDs[0]
            result.secondQuoteID = randomIDs[1]
            result.thirdQuoteID = randomIDs[2]
            db.session.commit()
        else:
            randomIDs = []
            result = UserModel.query.filter_by(id = userID).first()
            randomIDs.append(result.firstQuoteID)
            randomIDs.append(result.secondQuoteID)
            randomIDs.append(result.thirdQuoteID)

        result = []
        for quote_id in randomIDs:
            quote_query = QuoteModel.query.filter_by(id = quote_id).first()
            result.append(quote_query)
        print(result)
        return result


api.add_resource(UserData, "/UserGet/<int:userID>/<string:currentTime>/<string:setTime>")

if __name__ == "__main__":
    app.run()
    #Debug off

