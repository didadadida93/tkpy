from math import sqrt


regionIds = {
    cell_id(x, y): [
        cell_id(xx, yy) for xx in range(0+(x*7), 7+(x*7)) for yy in range(0+(y*7), 7+(y*7))
    ] for x in range(-13, 14) for y in range(-13, 14)
}


def cell_id(x, y):
    """ :func:`cell_id` will convert :class:`int` x and :class:`int` y
    into cell id that understand for TK.

    :param x: - :class:`int` x cell's coordinate.
    :param y: - :class:`int` y cell's coordinate.

    return: :class:`int`
    """
    return (536887296 + x) + (y * 32768)


def reverse_id(vid):
    """ :func:`reverse_id` will convert cell id into x, y tuple coordinate
    that read able for human.

    :param vid: - :class:`int` cell id

    return: :class:`tuple`
    """
    binary = f'{vid:b}'
    if len(binary) < 30:
        binary = '0' + binary
    xcord, ycord = binary[15:], binary[:15]
    realx = int(xcord, 2) - 16384
    realy = int(ycord, 2) - 16384
    return realx, realy


def distance(source, target):
    """ :func:`distance` for calculating distance between point.

    :param source: x, y tuple of source coordinates
    :param target: x, y tuple of target coordinates

    return: :class:`float`
    """
    return sqrt((source[0] - target[0])**2 + (source[1] - target[1])**2)


class Map:
    """ :class:`Map` is represent of map object for TK. Map data from TK
    is stored in here. This class provide an easy way to access map data
    by using :meth:`coordinate` for accessing specific cell based on their
    coordinate, or using :property:`villages` for yield cell that contains
    village data on it, or by using another property.

    Usage::
        >>> m = Map(driver)
        >>> m.pull()
        >>> m.coordinate(0, 0)
        <Cell({'id': '536887296', 'landscape': '9013', 'owner': '0'})>
        >>> villages = list(m.villages)
    """
    def __init__(self, client):
        self.client = client
        self._raw_data = dict()

    def __repr__(self):
        return str(type(self))

    def pull(self):
        """ :meth:`pull` for pulling map data from TK. """
        r = self.client.map.getByRegionIds({
            'regionIdCollection': {
                '1': list(regionIds.keys())
            }
        })
        self._raw_data.update(r)

    def pull_region_id(self, region_id=[]):
        """ :meth:`pull_region_id` will pull specific region data from 
        TK.

        :param region_id: - :class:`list` (optional) list of region id
                            that want to requested to TK. Default: []
        """
        r = self.client.map.getByRegionIds({
            'regionIdCollection': {
                '1': region_id
            }
        })
        self._raw_data.update(r)

    def gen_cell(self):
        """ :meth:`gen_cell` is a :func:`generator` that yield :class:`Cell`
        object.

        yield: :class:`Cell`
        """
        for c in self._raw_data['response']:
            try:
                for region_id in self._raw_data['response'][c]['region']:
                    for cell in self._raw_data['response'][c]['region'][region_id]:
                        # yield cell
                        yield Cell(self.client, cell)
            except:
                continue

    def gen_villages(self):
        """ :meth:`gen_villages` is a :func:`generator` that yield :class:`Cell`
        that have 'village' data on it.

        yield: :class:`Cell`
        """
        for cell in self.cell:
            if 'village' in cell:
                yield cell
            else:
                continue

    def gen_tiles(self):
        """ :meth:`gen_tiles` is a :func:`generator that yield :class:`Cell`
        known as Abandoned valley in game.

        yield: :class:`Cell`
        """
        for cell in self.cell:
            if 'village' not in cell and 'resType' in cell:
                yield cell
            else:
                continue

    def gen_oases(self):
        """ :meth:`gen_oases` is a :func:`generator` that yield :class:`Cell`
        that have 'oasis' data on it.

        yield: :class:`Cell`
        """
        for cell in self.cell:
            if 'oasis' in cell:
                yield cell
            else:
                continue

    def gen_wilderness(self):
        """ :meth:`gen_wilderness` is a :func:`generator` that yield :class:`Cell`
        alsow know as Wilderness in game.

        yield: :class:`Cell`
        """
        for cell in self.cell:
            if 'oasis' not in cell and 'resType' not in cell:
                yield cell
            else:
                continue

    def village(self, name=None, id=None, default={}):
        """ :meth:`village` is used for find specific :cell:`Cell` object
        that have village data on it based on village name or id.

        :param name: - :class:`str` village name.
        :param id: - :class:`int` village id.
        :param default: - :class:`dict` (optional) default value if :cell:`Cell` object
                          didn't found. Default: {}.

        return: :class:`Cell`
        """
        for village in self.villages:
            if village['id'] == str(id) or village['village']['name'] == name:
                return village
        return default

    def coordinate(self, x, y, default={}):
        """ :meth:`coordinate` is used for find specific :cell:`Cell` object
        based on cell's coordinate.

        :param x: - :class:`int` x cell's coordinate.
        :param y: - :class:`int` y cell's coordinate.
        :param default: - :class:`dict` (optional) default value if :cell:`Cell`
                          object didnt' found. Default: {}

        return: :class:`Cell`
        """
        for cell in self.cell:
            if cell['id'] == str(cell_id(x, y)):
                return cell
        return default

    def tile(self, id, default={}):
        """ :meth:`tile` is used for find specific :cell:`Cell` object
        based on cell's id.

        :param id: - :class:`int` cell id.
        :param default: - :class:`dict` (optional) default value if :cell:`Cell`
                          object didn't found. Default: {}

        return: :class:`Cell`
        """
        for cell in self.cell:
            if cell['id'] == str(id):
                return cell
        return default

    def gen_kingdoms(self):
        """ :meth:`gen_kingdoms` is a :func:`generator` that yield :class:`Kingdom`
        object.

        yield: :class:`Kingdom`
        """
        for c in self._raw_data['response']:
            try:
                for x in self._raw_data['response'][c]['kingdom']:
                    yield Kingdom(x, self._raw_data['response'][c]['kingdom'][x])
            except:
                continue

    def kingdom(self, name=None, id=None, default={}):
        """ :meth:`kingdom` is used for find :class:`Kingdom` object
        using name or id of kingdom.

        :param name: - :class:`str` kingdom's name.
        :param id: - :class:`int` kingdom's id.
        :param default: - :class:`dict` (optional) default value when
                          :class:`Kingdom` object not found. Default: {}

        return: :class:`Kingdom`
        """
        for kingdom in self.kingdoms:
            if kingdom.id == str(id) or kingdom.name == name:
                return kingdom
        return default

    def gen_players(self):
        """ :property:`gen_players` is a :func:`generator` that yield
        :class:`Player` object.

        yield: :class:`Player`
        """
        for c in self._raw_data['response']:
            try:
                for x in self._raw_data['response'][c]['player']:
                    yield Player(
                        self.client, x, self._raw_data['response'][c]['player'][x]
                    )
            except:
                continue

    def player(self, name=None, id=None, default={}):
        """ :meth:`player` is used for find :class:`Player` object
        used player name or id.

        :param name: - :class:`str` player's name.
        :param id: - :class:`int` player's id.
        :param default: - :class:`dict` (optional) default value when
                          :class:`Player` object not found. Default: {}

        return: :class:`Player`
        """
        for player in self.players:
            if player.id == str(id) or player.name == name:
                return player
        return default


class Cell:
    """ :class:`Cell` is a class that represent cell object. This class
    is where cell data stored.
    """
    def __init__(self, client, data):
        self.client = client
        self.data = data

    def __contains__(self, item):
        return self.data.__contains__(item)

    def __getitem__(self, key):
        try:
            return self.data[key]
        except:
            raise

    def __repr__(self):
        return f'<{type(self).__name__}({self.data})>'

    def details(self):
        """ :meth:`details` send requests to TK for perceive more details
        about this cell.

        return: :class:`dict`
        """
        r = self.client.cache.get({'names':[f'MapDetails:{self.id}']})
        return r['cache'][0]['data']

    @property
    def id(self):
        """ :property:`id` return this cell id. """
        return self.data['id']

    @property
    def coordinate(self):
        """ :property:`coordinate` return this cell coordinate. """
        return reverse_id(self.id)


class Player:
    """ :class:`Player` is represent of player object. This class is where
    player data stored.
    """
    def __init__(self, client, playerId, data):
        self.client = client
        self.id = playerId
        self.data = data
        self.data['playerId'] = playerId

    def __getitem__(self, key):
        try:
            return self.data[key]
        except:
            raise

    def __repr__(self):
        return f'<{type(self).__name__}({self.data})>'

    def hero_equipment(self):
        """ :meth:`hero_equipment` send requests to TK for perceive
        hero equipment of this player.

        return: :class:`dict`
        """
        return self.client.cache.get({
            'names': [f'Collection:HeroItem:{self.id}']
        })['cache'][0]['data']['cache']

    def details(self):
        """ :meth:`details` send requests to Tk for perceive this player
        details.

        return: :class:`dict`
        """
        return self.client.cache.get({
            'names': [f'Player:{self.id}']
        })['cache'][0]['data']

    @property
    def name(self):
        """ :property:`name` return this player name. """
        return self.data['name']

    @property
    def tribe_id(self):
        """ :property:`tribe_id` return this player tribe id. """
        return self.data['tribeId']

    @property
    def is_active(self):
        """ :property:`is_active` return whether this player is active or not.

        return: :class:`boolean`
        """
        if self.data['active'] == '1':
            return True
        return False


class Kingdom:
    """ :class:`Kingdom` represent of kingdom object. This class is where
    kingdom data stored.
    """
    def __init__(self, kingdomId, data):
        self.id = kingdomId
        self.data = data
        self.data['kingdomId'] = kingdomId

    def __getitem__(self, key):
        try:
            return self.data[key]
        except:
            raise

    def __repr__(self):
        return f'<{type(self).__name__}({self.data})>'

    @property
    def name(self):
        """ :property:`name` return this kingdom name. """
        return self.data['tag']
