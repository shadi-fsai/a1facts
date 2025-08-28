from neo4j import GraphDatabase

URI = "neo4j+s://82a2920f.databases.neo4j.io"
AUTH = ("neo4j", "E_ytyeg3qZqfnZxXv7AgBUEljyo5pqfV_VxDOdFWQp0")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

summary = driver.execute_query("""
    CREATE (a:Person {name: $name})
    CREATE (b:Person {name: $friendName})
    CREATE (a)-[:KNOWS]->(b)
    """,
    name="Alice", friendName="David",
    database_="neo4j",
).summary
print("Created {nodes_created} nodes in {time} ms.".format(
    nodes_created=summary.counters.nodes_created,
    time=summary.result_available_after
))

records, summary, keys = driver.execute_query("""
    MATCH (p:Person)-[:KNOWS]->(:Person)
    RETURN p.name AS name
    """,
    database_="neo4j",
)

# Loop through results and do something with them
for record in records:
    print(record.data())  # obtain record as dict

# Summary information
print("The query `{query}` returned {records_count} records in {time} ms.".format(
    query=summary.query, records_count=len(records),
    time=summary.result_available_after
))



driver = GraphDatabase.driver(URI, auth=AUTH)
session = driver.session(database="<database-name>")

# session/driver usage

session.close()
driver.close()