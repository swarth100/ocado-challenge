from container.container import Container
from item.item import Item
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

def getNewContainer(rule):
    newContainer = Container(rule)
    indexContainers.append(newContainer)

    return newContainer

def addAllSubcontainers(subs, main):
    for elem in subs:
        main.append(elem)

# Main method
if __name__ == '__main__':

    # Instantiate connection
    conn = DBsetup()

    # Instantiate view on DB
    initView(conn)

    # Get a list of available items
    for rule in range (1, 5):

        # Query data
        orderData = conn.execute("SELECT * FROM PRODUCT_ORDERS")
        container = Container(rule)

        # Setup global container
        for row in orderData:
            container.addItem(Item(rule, row))

            # - - - - - - - - - - - - - - - - - - - - -
        # Actual start of algorithm

        # Split the contents of the container
        # Initialise result list
        resContainer = []
        indexContainers = []

        curContainer = getNewContainer(rule)

        # Iterate through all items in global container
        for item in container.items:

            # Reset boolean conditions upon every iteration
            curContainerID = 0
            newCurContainer = False
            advanceCurContainer = False

            # On Container INDEX change
            if (item.orderID != curContainer.getLastItemOrder()) and (rule >= 2):

                # Add all the elements in the current buffer pool to the final containers
                addAllSubcontainers(indexContainers, resContainer)

                # Reset the current container
                indexContainers = []
                newCurContainer = True

            # Iterate through all Containers within the given bucket to find a container we can insert in
            while True:
                # Check for weights
                if (curContainer.getItemWeights() + item.weight >= 15) and (rule >= 3):
                    advanceCurContainer = True

                # Retrieve the next Container in the given container bucket
                if advanceCurContainer:
                    curContainerID += 1
                    if curContainerID >= len(indexContainers):
                        newCurContainer = True
                        advanceCurContainer = False
                    else:
                        curContainer = indexContainers[curContainerID]

                if not advanceCurContainer:
                    break

            # Create a new container for the given Bucket
            if newCurContainer:
                curContainer = getNewContainer(rule)

            # Add item to given container
            curContainer.addItem(item)

        # Add the last used container
        addAllSubcontainers(indexContainers, resContainer)

        # - - - - - - - - - - - - - - - - - - - - -

        result = resContainer

        # Remove the leading empty element
        result.pop(0)

        # Final printout
        print "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~"
        print "Rule: #" + str(rule)
        print "Necessary containers: " + str(len(result))
        print "Breakdown: "
        for i in range (0, len(result)):
            cont = result[i]
            print "C#" + str(i) + "\t |items: " + str(len(cont.items)) + "\t |ID: " + str(cont.getLastItemOrder()) + "  \t |weight: " + str(cont.getItemWeights())


    # Cleanup code
    cleanupView(conn)

    DBclose(conn)