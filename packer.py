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
        if len(elem) != 0:
            main.append(elem)

def splitOnRule(containers, rule):
    # Split on a given rule
    tmpConts = containers[:]

    for curRule in range (1, rule + 1):

        containers = tmpConts[:]
        tmpConts = []

        for subCont in containers:

            func = None
            if curRule == 2:
                func = spliOnRule2
            if curRule == 5:
                func = spliOnRule5
            if curRule == 6:
                func = spliOnRule6
            if curRule == 7:
                func = spliOnRule7

            if func != None:
                tmpRes = func(subCont.items, rule)
            else:
                tmpRes = [subCont]

            addAllSubcontainers(tmpRes, tmpConts)

    return tmpConts

def spliOnRule2(items, rule):
    oldID = 1

    res = []
    buff = Container()

    # Split in containers
    for item in items:

        # On Container INDEX change
        if (item.orderID != oldID):
            res.append(buff)
            oldID = item.orderID
            buff = Container()

        buff.addItem(item)

    res.append(buff)

    return res

def spliOnRule5(items, rule):
    res = []

    # Check for rule 5
    if rule >= 5:
        # Sort by segregation type
        items.sort(key=lambda x: x.category, reverse=False)

        splitInt = len(items)

        for i in range (1, splitInt):
            if items[i].category >= 5:
                splitInt = i
                break

        containerLeft = Container()
        addAllSubcontainers(items[splitInt:], containerLeft.items)
        res.append(containerLeft)

        containerRight = Container()
        addAllSubcontainers(items[:splitInt], containerRight.items)
        res.append(containerRight)

    else:
        newCont = Container()
        res = [newCont]
        addAllSubcontainers(items, newCont.items)

    return res

def spliOnRule6(items, rule):
    dryItems = [1, 2, 5, 6]
    res = []

    # Check for rule 6
    if rule >= 6:
        # Sort by segregation type
        items.sort(key=lambda x: x.category, reverse=False)

        containerLeft = Container()
        containerRight = Container()

        for item in items:
            if item.category in dryItems:
                containerLeft.items.append(item)
            else:
                containerRight.items.append(item)

        res.append(containerLeft)
        res.append(containerRight)

    else:
        newCont = Container()
        res = [newCont]
        addAllSubcontainers(items, newCont.items)

    return res

def spliOnRule7(items, rule):
    dryItems = [1, 2, 3, 5]
    res = []

    # Check for rule 7
    if rule >= 7:
        # Sort by segregation type
        items.sort(key=lambda x: x.category, reverse=False)

        containerLeft = Container()
        containerRight = Container()

        for item in items:
            if item.category in dryItems:
                containerLeft.items.append(item)
            else:
                containerRight.items.append(item)

        res.append(containerLeft)
        res.append(containerRight)

    else:
        newCont = Container()
        res = [newCont]
        addAllSubcontainers(items, newCont.items)

    return res

# Main method
if __name__ == '__main__':

    # Instantiate connection
    conn = DBsetup()

    # Instantiate view on DB
    initView(conn)

    # Get a list of available items
    for rule in range (1, 8):

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
        subContainers = splitOnRule([container], rule)

        for subCont in subContainers:

            if rule >= 3:
                # Sort contents based on weight
                subCont.items.sort(key=lambda x: x.weight, reverse=True)

            if rule >= 4:
                # Sort contents based on volume
                subCont.items.sort(key=lambda x: x.volume, reverse=True)

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

                    # Check for volumes (rule 4)
                    if (getCurContainer(curContainerID, indexContainers).getItemVolumes() + item.volume >= 65340) and (rule >= 4):
                        advanceCurContainer = True

                    # Check for weights (rule 3)
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
            print "C#" + str(i) + " \t|items: " + str(len(cont.items)) + "\t|ID: " + str(cont.getLastItemOrder()) + "\t|W: " + str(cont.getItemWeights()) + " \t|V: " + str(cont.getItemVolumes()) + " \t|SG: " + str(cont.getSeg()) + " \t|DW: " + str(cont.getDry())


    # Cleanup code
    cleanupView(conn)

    DBclose(conn)