from container.container import Container
from item.item import Item
from splitter.splitter import Splitter
import sqlite3

# Setup the database connection
def DBsetup():
    # Connect to the local database
    return sqlite3.connect('database.db')

# Destroy the database connection
def DBclose(conn):
    # Close the connection at the end
    conn.close()

# Initialise the product-item view
def initView(conn):
    # Create a temporary view
    try:
        conn.execute("CREATE VIEW PRODUCT_ORDERS AS SELECT * FROM PRODUCTS JOIN ORDERS ON PRODUCTS.ID = ORDERS.PRODUCTID")
        conn.commit()
    except sqlite3.OperationalError:
        print "View already present"

# Cleanup the product-item view
def cleanupView(conn):
    # Drop the temporary view
    conn.execute("DROP VIEW PRODUCT_ORDERS")
    conn.commit()

def newContainer(indexContainers):
    newContainer = Container()
    indexContainers.append(newContainer)

def getCurContainer(index, list):
    return list[index]

def addAllSubcontainers(subs, main):
    for elem in subs:
        main.append(elem)

def spliOnRule1(items, rule):
    oldID = 1

    res = []
    buff = Container()

    # Split in containers
    for item in items:

        # On Container INDEX change
        if (item.orderID != oldID) and (rule >= 2):
            res.append(buff)
            oldID = item.orderID
            buff = Container()

        buff.addItem(item)

    res.append(buff)

    return res

def spliOnRule4(items, rule):
    oldID = 1

    res = []
    buff = Container()

    # Split in containers
    for item in items:

        # On Container INDEX change
        if (item.orderID != oldID) and (rule >= 2):
            res.append(buff)
            oldID = item.orderID
            buff = Container()

        buff.addItem(item)

    res.append(buff)

    return res

# Main method
if __name__ == '__main__':

    # Instantiate connection
    conn = DBsetup()

    # Instantiate view on DB
    initView(conn)

    # Get a list of available items
    for rule in range (1, 6):

        # Query data
        orderData = conn.execute("SELECT * FROM PRODUCT_ORDERS")
        container = Container()

        # Setup global container
        for row in orderData:
            container.addItem(Item(rule, row))

        # - - - - - - - - - - - - - - - - - - - - -
        # Actual start of algorithm

        result = []

        # Split on Rule 1
        subContainers = spliOnRule1(container.items, rule)

        for subCont in subContainers:

            if rule >= 4:
                # Sort by segregation type
                subCont.items.sort(key=lambda x: x.category, reverse=False)

            # Split on Rule 4
            #subContainers = spliOnRule1(container.items, rule)

            if rule == 3:
                # Sort contents based on weight
                subCont.items.sort(key=lambda x: x.weight, reverse=True)
            elif rule == 5:
                # Sort contents based on volume
                subCont.items.sort(key=lambda x: x.volume, reverse=False)

            # Split the contents of the container
            # Initialise result list
            indexContainers = []

            newContainer(indexContainers)

            # Iterate through all items in global container
            for item in subCont.items:

                # Reset boolean conditions upon every iteration
                curContainerID = 0
                newCurContainer = False

                # Iterate through all Containers within the given bucket to find a container we can insert in
                while True:

                    advanceCurContainer = False

                    # Check for weights
                    if (getCurContainer(curContainerID, indexContainers).getItemWeights() + item.weight >= 15.0) and (rule >= 3):
                        advanceCurContainer = True

                    # Retrieve the next Container in the given container bucket
                    if advanceCurContainer:

                        # Increase the lookIn bucket by one
                        curContainerID += 1

                        # Check if the new bucket is already initialised.
                        # Else exit the loop and create a new Container for said bucket
                        if curContainerID >= len(indexContainers):
                            newCurContainer = True
                            advanceCurContainer = False

                    if not advanceCurContainer:
                        break

                # Create a new container for the given Bucket
                if newCurContainer:
                    newContainer(indexContainers)

                # Add item to given container
                getCurContainer(curContainerID, indexContainers).addItem(item)

            # Add the last used container
            addAllSubcontainers(indexContainers, result)

        # - - - - - - - - - - - - - - - - - - - - -

        # Remove the leading empty element

        # Final printout
        print "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~"
        print "Rule: #" + str(rule)
        print "Necessary containers: " + str(len(result))
        for i in range (0, len(result)):
            cont = result[i]
            print "C#" + str(i) + " \t|items: " + str(len(cont.items)) + "\t |ID: " + str(cont.getLastItemOrder()) + "  \t |weight: " + str(cont.getItemWeights())


    # Cleanup code
    cleanupView(conn)

    DBclose(conn)