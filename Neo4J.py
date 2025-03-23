from flask import Flask, jsonify
from neo4j import GraphDatabase
from flask import request
 
 
 
def create_app():
 
    app = Flask(__name__)
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "asdfzxcv1"))
 
    # Naujo miesto registravimas
    @app.route('/cities', methods=['PUT'])
    def create_city():
        data = request.get_json()
        city = data['name']
        country = data['country']
 
        if not city or not country:
            return {"message": "City and country are required."}, 400
 
        with driver.session() as session:
            query = (
                "MATCH (c:City {name: $city, country: $country}) "
                "RETURN c"
            )
            result = session.run(query, city=city, country=country)
            if result.single():
                return {"message": "City already exists."}, 400
 
            query = (
                "CREATE (c:City {name: $city, country: $country}) "
                "RETURN c"
            )
            session.run(query, city=city, country=country)
 
            return {"message": "City registered successfully"}, 204
       
 
    # Gauti visus miestus
    @app.route('/cities', methods=['GET'])
    def get_cities():
 
        country_filter = request.args.get('country')
 
        with driver.session() as session:
            if country_filter:
                query = "MATCH (c:City) WHERE c.country = $country RETURN c.name AS name, c.country AS country"
                result = session.run(query, country=country_filter)
            else:
                query = "MATCH (c:City) RETURN c.name AS name, c.country AS country"
                result = session.run(query)
 
            locations = []
            for record in result:
                locations.append({"name": record["name"], "country": record["country"]})
 
        return locations, 200
   

    # Gauti miestą pagal vardą
    @app.route('/cities/<name>', methods=['GET'])
    def get_city(name):
        with driver.session() as session:
            query = "MATCH (c:City {name: $name}) RETURN c.name AS name, c.country AS country"
            result = session.run(query, name=name)
 
            if not result.peek():
                return {"message": "City not found."}, 404
 
            for record in result:
                return{"name": record["name"], "country": record["country"]}, 200
 
 
    # Registruoti naują oro uostą
    @app.route('/cities/<name>/airports', methods=['PUT'])
    def create_airport(name):
        data = request.get_json()
        code = data.get('code')
        airport = data.get('name')
        numberOfTerminals = data.get('numberOfTerminals')
        address = data.get('address')

        if not code or not airport or not numberOfTerminals or not address:
            return {"message": "All fields are required"}, 400

        if not isinstance(numberOfTerminals, int) or numberOfTerminals <= 0:
            return {"message": "Number of terminals must be a positive integer"}, 400

        with driver.session() as session:

            city_check_query = "MATCH (c:City {name: $name}) RETURN c"
            city_check_result = session.run(city_check_query, name=name)
            if not city_check_result.single():
                return {"message": "City not found."}, 400

            airport_check_query = "MATCH (a:Airport {code: $code}) RETURN a"
            airport_check_result = session.run(airport_check_query, code=code)
            if airport_check_result.single():
                return {"message": "Airport already exists."}, 400

            create_query = (
                "MATCH (c:City {name: $name}) "
                "WITH c "
                "CREATE (a:Airport {code: $code, name: $airport, numberOfTerminals: $numberOfTerminals, address: $address}) "
                "MERGE (c)-[:HAS]->(a) "
                "RETURN a"
            )
            session.run(create_query, name=name, code=code, airport=airport, numberOfTerminals=numberOfTerminals, address=address)

            return {"message": "Airport created."}, 204



    # Gauti oro uostus pagal miestą
    @app.route('/cities/<name>/airports', methods=['GET'])
    def get_airports(name):
        with driver.session() as session:
            
            query = (
                "MATCH (c:City {name: $name})-[:HAS]->(a:Airport)"
                "RETURN a.code AS code, a.name AS name, a.numberOfTerminals AS numberOfTerminals, a.address AS address")
            result = session.run(query, name=name)
            airports = [{"code": record["code"], "name": record["name"], "numberOfTerminals": record["numberOfTerminals"], "address": record["address"]} for record in result]
        return airports, 200
   

    # Gauti oro uostą pagal kodą
    @app.route('/airports/<code>', methods=['GET'])
    def get_airport(code):
        with driver.session() as session:
 
            airport_check_query = "MATCH (a:Airport {code: $code}) RETURN a"
            airport_check_result = session.run(airport_check_query, code=code)
            if not airport_check_result.single():
                return {"message": "Airport not found."}, 404
 
            query = (
                "MATCH (a:Airport {code: $code})<-[:HAS]-(c:City)"
                "RETURN a.code AS code, c.name AS city, a.name AS name, a.numberOfTerminals AS numberOfTerminals, a.address AS address"
                )
            result = session.run(query, code=code)
            for record in result:
                return{"code": record["code"], "city":record["city"], "name": record["name"], "numberOfTerminals": record["numberOfTerminals"], "address": record["address"]}, 200
 
   
    # Registruoti naują skrydį
    @app.route('/flights', methods=['PUT'])
    def create_flight():
        data = request.get_json()
        number = data['number']
        fromAirport = data['fromAirport']
        toAirport = data['toAirport']
        price = data['price']
        flightTimeInMinutes = data['flightTimeInMinutes']
        operator = data['operator']
 
        if not number or not fromAirport or not toAirport or not price or not flightTimeInMinutes or not operator:
            return {"message": "Missing data."}, 400
 
        with driver.session() as session:
            query = (
                "MATCH (a1:Airport {code: $fromAirport}), (a2:Airport {code: $toAirport}) "
                "RETURN count(a1) AS countFrom, count(a2) AS countTo"
            )
            result = session.run(query, fromAirport=fromAirport, toAirport=toAirport).single()
            if result["countFrom"] == 0 or result["countTo"] == 0:
                return {"message": "One or both airports do not exist."}, 410
            
            query = (
            "MATCH (a1:Airport {code: $fromAirport})-[:FLIES_TO]->(f:Flight {number: $number, operator: $operator})-[:FLIES_TO]->(a2:Airport {code: $toAirport}) "
            "RETURN f")
            existing_flight = session.run(query, number=number, operator=operator, fromAirport=fromAirport, toAirport=toAirport).single()
            if existing_flight:
                return {"message": "Flight with the same number, operator, and route already exists."}, 400

            query = (
                "MATCH (a1:Airport {code: $fromAirport}), (a2:Airport {code: $toAirport}) "
                "CREATE (f:Flight {number: $number, price: $price, flightTimeInMinutes: $flightTimeInMinutes, operator: $operator}) "
                "MERGE (a1)-[:FLIES_TO]->(f) "
                "MERGE (f)-[:FLIES_TO]->(a2) "
                "RETURN f"
            )
            session.run(query, number=number, fromAirport=fromAirport, toAirport=toAirport, price=price, flightTimeInMinutes=flightTimeInMinutes, operator=operator)
            return {"message": "Flight created."}, 204
 
   
    # Gauti skrydį pagal numerį
    @app.route('/flights/<code>', methods=['GET'])
    def get_flight(code):
        with driver.session() as session:
            query = (
                "MATCH (f:Flight {number: $code})"
                "MATCH (a1:Airport)-[:FLIES_TO]->(f)"
                "MATCH (f)-[:FLIES_TO]->(a2:Airport)"
                "MATCH (a1)<-[:HAS]-(c1:City)"
                "MATCH (a2)<-[:HAS]-(c2:City)"
                "RETURN f.number AS number, a1.code AS fromAirport, c1.name AS fromCity, a2.code AS toAirport, c2.name AS toCity, f.price AS price, f.flightTimeInMinutes AS flightTimeInMinutes, f.operator AS operator"
           )
            result = session.run(query, code=code)
            if not result.peek():
                return {"message": "Flight not found."}, 404
            for record in result:
                return {
                    "number": record["number"],
                    "fromAirport": record["fromAirport"],
                    "fromCity": record["fromCity"],
                    "toAirport": record["toAirport"],
                    "toCity": record["toCity"],
                    "price": record["price"],
                    "flightTimeInMinutes": record["flightTimeInMinutes"],
                    "operator": record["operator"]
                }, 200


    # Gauti skrydžius tarp dviejų miestų
    @app.route('/search/flights/<fromCity>/<toCity>', methods=['GET'])
    def search_flights(fromCity, toCity):
        with driver.session() as session:
            query = (
                """
                MATCH (c1:City {name: $fromCity})-[:HAS]->(a1:Airport)
                MATCH (c2:City {name: $toCity})-[:HAS]->(a2:Airport)
 
                MATCH p = (a1)-[:FLIES_TO*]->(f:Flight)-[:FLIES_TO*]->(a2)
                WHERE length(p) >= 2 AND length(p) <= 4
 
                RETURN
                    a1.code AS fromAirport,
                    a2.code AS toAirport,
                    collect(DISTINCT f.number) AS flightNumbers,
                    SUM(f.price) AS price,
                    SUM(f.flightTimeInMinutes) AS flightTime,
                    length(p)-1 AS stops
                """
            )
 
            result = session.run(query, fromCity=fromCity, toCity=toCity)
 
            flights = [
                {
                    "fromAirport": record["fromAirport"],
                    "toAirport": record["toAirport"],
                    "flights": record["flightNumbers"],  
                    "price": record["price"],
                    "flightTimeInMinutes": record["flightTime"],
                }
                for record in result
            ]
           
        if not flights:
            return {"message": "No flights found between the specified cities."}, 404
 
        return flights, 200
 

    # Išvalyti duomenų bazę
    @app.route('/cleanup', methods=['POST'])
    def reset():
        with driver.session() as session:
            query = "MATCH (n) DETACH DELETE n"
            session.run(query)
        return {"message": "Cleanup successful."}, 200
       
 
 
    return app