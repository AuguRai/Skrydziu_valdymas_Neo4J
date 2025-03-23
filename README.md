Šis web servisas naudodamas Neo4j duomenų bazę pritaiko operacijas skrydžių valdymui. 
Programoje galima registruoti miestus ir oro uostus, ieškoti skrydžių tarp miestų, gauti informaciją apie oro uostus ir skrydžius, atlikti paiešką pagal skrydžių numerį ar maršrutą.
Įdiegta galimybė išvalyti visus duomenis iš duomenų bazės.


## Programos paleidimas

Vienas iš būdų paleisti programą naudojant Docker Desktop:

Atsisiųskite ir susidiekite Docker Desktop
Pasileiskite Docker konteinerį: cypher-shell -u neo4j -p password --address localhost --port 7687

Web serviso testavimui galima naudoti Postman programą.

## **Operacijos miestams**

/cities (PUT) - leidžia įterpti naują miestą į duomenų bazę. Pateikiami privalomi duomenys: miesto pavadinimas ir šalis.

/cities (GET) -gali gauti visus miestus arba filtruoti pagal šalį.

/cities/<name> (GET) - grąžina informaciją apie konkretų miestą pagal pavadinimą (miesto pavadinimas yra URL parametras).

## **Operacijos oro uostams**

/cities/<name>/airports (PUT) - registruoja naują oro uostą pagal miestą. Pateikiami oro uosto kodas, pavadinimas, terminalų skaičius ir adresas.

/cities/<name>/airports (GET) - grąžina visus oro uostus, esančius nurodytame mieste.

/airports/<code> (GET) - grąžina oro uosto informaciją pagal jo kodą.

## **Operacijos skrydžiams**

/flights (PUT) - registruoja naują skrydį, įskaitant skrydžio numerį, pradinį ir galutinį oro uostą, kainą, skrydžio trukmę ir operatorių.

/flights/<code> (GET) - grąžina informaciją apie konkretų skrydį pagal skrydžio numerį, įskaitant tiek oro uostus, tiek miestus.

/search/flights/<fromCity>/<toCity> (GET) - grąžina visus skrydžius su papildomais informacija apie kainą, skrydžio laiką ir tarpinius sustojimus.

## **Papildomos funkcijos**

/cleanup (POST) - išvalo visus įrašus duomenų bazėje.
