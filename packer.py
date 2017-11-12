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

def newContainer(sibling, indexContainers):
    if sibling.parent:
        newContainer = sibling.generateSiblingContainer()
    else:
        newContainer = sibling.generateChildContainer()
    indexContainers.append(newContainer)

def getCurContainer(index, list):
    return list[index]

def addAllSubcontainers(subs, main):
    for elem in subs:
        if len(elem) != 0:
            main.append(elem)
        else:
            elem.kill()

# Method to split the given macroContainer given a set of rules
def splitOnRule(containers, rule):
    # Split on a given rule
    tmpConts = containers[:]

    for curRule in range (1, rule + 1):

        containers = tmpConts[:]
        tmpConts = []

        for subCont in containers:

            # Define a function to apply at a given step
            func = None
            if curRule == 2:
                func = lambda x: x.getRule2Set()
            if curRule == 3:
                subCont.items.sort(key=lambda x: x.weight, reverse=True)
            if curRule == 4:
                subCont.items.sort(key=lambda x: x.volume, reverse=True)
            if curRule == 5:
                func = lambda x: x.getRule5Set()
            if curRule == 6:
                func = lambda x: x.getRule6Set()
            if curRule == 7:
                func = lambda x: x.getRule7Set()
            if func == None:
                func = lambda x: [x]

            # Apply the function and update the set of newly obtained containers
            tmpRes = func(subCont)
            addAllSubcontainers(tmpRes, tmpConts)

    return tmpConts

def iterateThroughContainers(parent, indexContainers, rule):

    newCurContainer = False

    # Reset boolean conditions upon every iteration
    curContainerID = 0

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
        newContainer(parent, indexContainers)

    # Add item to given container
    getCurContainer(curContainerID, indexContainers).addItem(item)

    return curContainerID

# Main method
if __name__ == '__main__':

    # Instantiate connection
    conn = DBsetup()

    # Instantiate view on DB
    initView(conn)

    # Get a list of available items
    for rule in range(1, 9):

        # Query data
        orderData = conn.execute("SELECT * FROM PRODUCT_ORDERS")
        rootContainer = Container()

        # Setup global container
        for row in orderData:
            rootContainer.addItem(Item(rule, row))

        # - - - - - - - - - - - - - - - - - - - - -
        # Actual start of algorithm

        result = []

        excludedCategory = []
        newIndexContainers = []

        # Split on Rule 1
        subContainers = splitOnRule([rootContainer], rule)

        subContainers.append(Container())

        subContParent = None

        for subCont in subContainers:

            if subCont.parent != subContParent and (rule >= 8) and subContParent:

                if len(newIndexContainers) == 0:
                    newContainer(subContParent.children[0], newIndexContainers)

                # Iterate through all previously excluded items
                for item in excludedCategory:

                    iterateThroughContainers(subContParent.children[0], newIndexContainers, rule)

                    # Add the last used container
                addAllSubcontainers(newIndexContainers, result)

                subContParent = subCont.parent
                excludedCategory = []
                newIndexContainers = []

            # Split the contents of the container
            # Initialise result list
            indexContainers = []

            newContainer(subCont, indexContainers)
            subCont.kill()

            contentCat = 0

            # Iterate through all items in global container
            for item in subCont.items:

                contentCat = item.category

                # Skip 7s and add them later on
                if (rule >= 8) and (item.category == 7):
                    excludedCategory.append(item)
                    continue
                else:
                    curContainerID = iterateThroughContainers(subCont, indexContainers, rule)

            # Add the last used container
            if ((contentCat == 4) or (contentCat == 7) or (contentCat == 8)) and (rule >= 8):
                addAllSubcontainers(indexContainers, newIndexContainers)
            else:
                addAllSubcontainers(indexContainers, result)

            subContParent = subCont.parent

        # - - - - - - - - - - - - - - - - - - - - -

        # Remove the leading empty element

        #print "FINAL CHILD NUMBER"

        #print len(rootContainer.children)

        #for elem in rootContainer.children:
        #    print "--"
        #    print len(elem.children)
        #    print "-"

        #    for c in elem.children:
        #        print len(c.children)

        # Final printout
        print "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~"
        print "Rule: #" + str(rule)
        print "Necessary containers: " + str(len(result))
        for i in range (0, len(result)):
            cont = result[i]
            print "C#" + str(i) + " \t|items: " + str(len(cont.items)) + "\t|ID: " + str(cont.getLastItemOrder()) + "\t|W: " + str(cont.getItemWeights()) + " \t|V: " + str(cont.getItemVolumes()) + " \t|SG: " + str(cont.getRule5Value()) + " \t|DW: " + str(cont.getRule6Value())


    # Cleanup code
    cleanupView(conn)

    DBclose(conn)