__author__ = 'donatm'

# graph is in adjacent list representation

def highlightPath(mapModel, fromRoom, toRoom):

    print toRoom

    oldPath = mapModel.getPath()

    for roomId in oldPath:
        room = mapModel.rooms()[roomId]
        room.setHighlight(False)
        room.getView().update()

    if fromRoom is None:
        return

    if toRoom not in mapModel.rooms():
        return

    path = findPath(mapModel, fromRoom, mapModel.rooms()[toRoom])
    mapModel.setPath(path)
    for roomId in path:
        room = mapModel.rooms()[roomId]
        room.setHighlight(True)
        room.getView().update()

    print path


def findPath(mapModel, fromRoom, toRoom):
    log = []
    queue = []
    queue.append([fromRoom.getId()])
    while queue:
        # get the first path from the queue
        path = queue.pop(0)
        # get the last node from the path
        node = path[-1]
        # path found
        log.append(node)
        if node == toRoom.getId():
            return path
        # enumerate all adjacent nodes, construct a new path and push it into the queue
        for adjacent in mapModel.rooms()[node].getLinks().itervalues():
            destination = adjacent.getDestinationFor(mapModel.rooms()[node])
            if destination.getId() in log:
                continue
            new_path = list(path)
            new_path.append(destination.getId())
            queue.append(new_path)
            log.append(destination.getId())

    return []

def d_highlightPath():
    pass