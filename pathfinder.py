__author__ = 'donatm'

# graph is in adjacent list representation

def highlightPath(mapModel, fromRoom, toRoom):
    path = findPath(mapModel, fromRoom, toRoom)

    for roomId in path:
        room = mapModel.rooms()[roomId]
        room.setProperty(room.PROP_COLOR, '#23FF00')
        room.getView().update()


def findPath(mapModel, fromRoom, toRoom):
    queue = []
    queue.append([fromRoom.getId()])
    while queue:
        # get the first path from the queue
        path = queue.pop(0)
        # get the last node from the path
        node = path[-1]
        # path found
        mapModel.rooms()[node].setProperty(toRoom.PROP_COLOR, '#FFFFFF')
        mapModel.rooms()[node].getView().update()
        if node == toRoom.getId():
            return path
        # enumerate all adjacent nodes, construct a new path and push it into the queue
        for adjacent in mapModel.rooms()[node].getLinks().itervalues():
            destination = adjacent.getDestinationFor(mapModel.rooms()[node])
            new_path = list(path)
            new_path.append(destination.getId())
            queue.append(new_path)



