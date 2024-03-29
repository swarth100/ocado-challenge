from container.container import Container
from item.item import Item
from container.point import Point
from container.prism import Prism
import sqlite3

import time

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
        print("View already present")

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

def iterateThroughContainers(parent, item, indexContainers, rule):
    # By default to not extend list of containers
    newCurContainer = False

    preventValueSave = False

    # Reset boolean conditions upon every iteration
    curContainerID = 0

    # Iterate through all Containers within the given bucket to find a container we can insert in
    while True:

        advanceCurContainer = False

        curContainer = getCurContainer(curContainerID, indexContainers)

        # Check for invalid data
        if (item.volume >= 65340) or (item.weight >= 15.0) or (item.height > 33) or (item.width > 36) or (item.length) > 55:
            preventValueSave = True
            break

        # Check for volumes (rule 4)
        if (curContainer.getItemVolumes() + item.volume >= 65340) and (rule >= 4):
            advanceCurContainer = True

        # Check for weights (rule 3)
        if (curContainer.getItemWeights() + item.weight >= 15.0) and (rule >= 3):
            advanceCurContainer = True

        if (rule >= 9):

            EPSILON = 0.01

            # Initialise the minimal steps to perform
            stepZ = max(item.height, 0) + EPSILON
            dZ = item.height / 2.0

            dY = item.length / 2.0

            stepX = max(item.width, 0) + EPSILON
            dX = item.width / 2.0

            # Initiate rotation checks for rule 10
            RANGE_MAX = 1
            rot = 0
            if (rule >= 10):
                RANGE_MAX = 4

            isMatch = False
            while (rot < RANGE_MAX) and not isMatch :
                # Iterate through all pierce points
                pz = dZ + EPSILON
                while (pz <= curContainer.height - dZ) and not isMatch:
                    px = dX + EPSILON
                    while (px <= curContainer.width - dX) and not isMatch:

                        # Determine the depth intercepts
                        depthIntercepts = curContainer.getNextCoord(
                                lambda x: filter(lambda y: y.isInRange(px, pz), x)
                                )

                        prism = None
                        # Retrieve the value of intercepts perpendicular to the Y-axis
                        for intercept in depthIntercepts:
                            point = Point(px, intercept.getMaxY() + dY + EPSILON, pz)

                            prism = Prism(item.height, item.length, item.width, point)

                            # Rot values greater than 0 only occur for rule >= 10
                            if rot == 1:
                                prism.rotateHorizontal()
                            elif rot == 2:
                                prism.rotateVerticle()
                            elif rot == 3:
                                prism.rotateDepth()

                            # Check that the prism can fit in the container for said position
                            for edge in prism.points:
                                if not curContainer.prism.contains(edge):
                                    prism = None
                                    break

                        isInCollision = False

                        if prism:
                            # Initiate comparison checks
                            for element in curContainer.prisms:

                                # Check that none of our current edges are contained in another prism
                                for edge in prism.points:
                                    if element.contains(edge):
                                        isInCollision = True
                                        break

                                # Check that none of other prism points are contained in us
                                for edge in element.points:
                                    if prism.contains(edge):
                                        isInCollision = True
                                        break

                                # Break loop at first detected collision
                                if isInCollision:
                                    break

                            # If no collision is detected proceed to add the mapping
                            if not isInCollision:
                                curContainer.prisms.append(prism)
                                # print "Mapped ID: " + str(item.productID)
                                # print prism
                                isMatch = True

                        # Increase step on x-axis
                        px += stepX

                    # Increase step on z-axis
                    pz += stepZ

                rot += 1

            if not isMatch:
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

    # Add item to given container found via ID
    if not preventValueSave:
        getCurContainer(curContainerID, indexContainers).addItem(item)

# Main method
if __name__ == '__main__':

    # Instantiate connection
    conn = DBsetup()

    # Instantiate view on DB
    initView(conn)

    # Get a list of available items
    for rule in range(1, 11):

        # Query data
        orderData = conn.execute("SELECT * FROM PRODUCT_ORDERS WHERE ORDERID <= 25")
        rootContainer = Container()

        # Setup global container
        for row in orderData:
            rootContainer.addItem(Item(rule, row))

        # - - - - - - - - - - - - - - - - - - - - -
        # Actual start of algorithm

        # Initialise result array
        result = []

        # Split on Rule 1
        subContainers = splitOnRule([rootContainer], rule)

        subContainers.append(Container())

        # Initialise Rule 8 variables
        subContParent = None
        excludedChild = None
        excludedCategory = []
        excludedIndexContainers = []


        # Iterate through the list of containers
        for subCont in subContainers:

            # Check if the global parent has changed.
            # Should it have we must post-process a lot of the data
            if subCont.parent != subContParent and (rule >= 8) and subContParent and excludedChild:

                # Initialise containers to one should the list be empty
                if len(excludedIndexContainers) == 0:
                    newContainer(excludedChild, excludedIndexContainers)

                # Iterate through all previously excluded items
                for item in excludedCategory:

                    # print "ENTERING WITH RULE: " + str(rule)
                    iterateThroughContainers(subContParent.children[0], item, excludedIndexContainers, rule)

                    # Add the last used container
                addAllSubcontainers(excludedIndexContainers, result)

                # Re-initialise categories to empty status
                excludedCategory = []
                excludedIndexContainers = []
                excludedChild = None

            # Split the contents of the container
            # Initialise result list
            indexContainers = []

            # Set pointer values
            subContParent = subCont.parent

            newContainer(subCont, indexContainers)
            subCont.kill()

            contentCat = 0

            # Iterate through all items in global container
            for item in subCont.items:

                contentCat = item.category

                if (rule >= 8) and (item.category == 7):
                    # Skip 7s and add them to a list of excluded items
                    excludedCategory.append(item)
                    if not excludedChild:
                        excludedChild = subCont
                else:
                    # Record all other values normally
                    iterateThroughContainers(subCont, item, indexContainers, rule)

            # Add the last used container
            if ((contentCat == 4) or (contentCat == 7) or (contentCat == 8)) and (rule >= 8):
                addAllSubcontainers(indexContainers, excludedIndexContainers)
            else:
                addAllSubcontainers(indexContainers, result)

        print("Finished A RULE")

        # - - - - - - - - - - - - - - - - - - - - -
        # Final printout

        totVol = 0
        totWei = 0

        print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
        print("Rule: #" + str(rule))
        for i in range (0, len(result)):
            cont = result[i]
            totVol += cont.getItemVolumes()
            totWei += cont.getItemWeights()
            print("C#" + str(i) + " \t|items: " + str(len(cont.items)) + \
                    "\t|ID: " + str(cont.getLastItemOrder()) + \
                    "\t|W: " + str(cont.getItemWeights()) + \
                    " \t|V: " + str(cont.getItemVolumes()) + \
                    " \t|SG: " + str(cont.getRule5Value()) + \
                    " \t|DW: " + str(cont.getRule6Value()) + \
                    "\t|#: " + str(cont.getCategories()))
                    #"   \t|>: " + str(cont.getProductIDs()))
        print("Necessary containers: " + str(len(result)))
        print("CHECKSUM: " + str(totVol) + " " + str(totWei))

        #with open('./output/SSPack_rule_9.csv', 'w') as f:
        #    print('ORDER_ID,CONTAINER_ID,SKU_ID', file=f)
        #    for i in range(0, len(result)):
        #        cont = result[i]
        #        order_id = str(cont.getLastItemOrder())
        #        cont_id = str(i)
        #        for product_id in cont.getProductIDs():
        #            print(order_id + ',' + cont_id + ',' + str(product_id), file=f)

    # Cleanup code
    cleanupView(conn)

    DBclose(conn)
