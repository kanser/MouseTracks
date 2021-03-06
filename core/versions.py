"""
This is part of the Mouse Tracks Python application.
Source: https://github.com/Peter92/MouseTracks
"""

from __future__ import absolute_import

import time

import core.numpy as numpy
from core.compatibility import get_items, unicode


VERSION_HISTORY = [
    '-1',
    '2.0',
    '2.0.1',
    '2.0.1b',
    '2.0.2',
    '2.0.3',
    '2.0.4',
    '2.0.5',
    '2.0.5b',
    '2.0.6',
    '2.0.6b',
    '2.0.6c',
    '2.0.7',
    '2.0.8',
    '2.0.9',
    '2.0.9b',
    '2.0.9c',
    '2.0.9d',
    '2.0.9e',
    '2.0.10',
    '2.0.10b',
    '2.0.10c',
    '2.0.10d',
    '2.0.11',
    '2.0.12',
    '2.0.13'
]

VERSION = VERSION_HISTORY[-1]


class IterateMaps(object):
    def __init__(self, maps):
        self.maps = maps
        
    def _iterate(self, maps, command, extra=None, _legacy=False):            
        for key, value in get_items(maps):
            
            #Old format where resolution was separate for each map
            if _legacy and isinstance(key, (str, unicode)):
                self._iterate(value, command, extra, _legacy=_legacy)
            
            #New format when each resolution contains all the maps
            elif not _legacy and isinstance(value, dict):
                self._iterate(value, command, extra, _legacy=_legacy)

            #Separate the numpy arrays from the data
            elif command == 'separate':
                array = maps[key]
                maps[key] = len(self._map_list)
                self._map_list.append(array)
            
            #Rejoin the numpy arrays with the data
            elif command == 'join':
                maps[key] = extra[value]
            
            #Convert dicts to numpy arrays (only used on old files)
            elif command == 'convert' and _legacy:
                width, height = key
                numpy_array = numpy.array((width, height), create=True, dtype='int64')
                for x, y in value:
                    numpy_array[y][x] = value[(x, y)]
                maps[key] = numpy_array
                
    def separate(self):
        """Separate the numpy maps from the main data, and replace with an integer."""
        self._map_list = []
        self._iterate(self.maps, 'separate')
        return self._map_list

    def join(self, numpy_maps, _legacy=False):
        """Merge with the numpy maps again."""
        self._iterate(self.maps, 'join', numpy_maps, _legacy=_legacy)
    
    def convert(self):
        """Convert the old map dictionaries to numpy arrays."""
        self._iterate(self.maps, 'convert', _legacy=True)
        
        
def _get_id(id):
    """Read the ID for upgrading versions.
    If no ID exists, such as if the version may not be finished,
    it'll default to the first ID and not upgrade.
    """
    try:
        return VERSION_HISTORY.index(str(id))
    except ValueError:
        return 0


def upgrade_version(data={}, update_metadata=True):
    """Files from an older version will be run through this function.

    History:
    2.0: Base script
    2.0.1: Add acceleration tracking
    2.0.1b: Rename acceleration to speed, change tracking method
    2.0.2: Experimenting with combined speed and position tracks
    2.0.3: Separate click maps, record both keys pressed and how long
    2.0.4: Save creation date and rename modified date
    2.0.5: Group maps and add extras for experimenting on
    2.0.5b: Separate tick counts for different maps
    2.0.6: Remove speed and combined maps as they don't look very interesting
    2.0.6b: Record when session started
    2.0.6c: Record key presses per session
    2.0.7: Fixed some incorrect key names
    2.0.8: Store each session start
    2.0.9: Remove invalid track coordinates
    2.0.9b: Matched format of session and total ticks, converted all back to integers
    2.0.9c: Created separate map for clicks this session
    2.0.9d: Remove temporary maps as they were messy, add double clicks to test
    2.0.9e: Maintainence to remove invalid resolutions (the last update caused a few)
    2.0.10: Rearrange some maps and convert to numpy arrays
    2.0.10b: Reset double click maps for code update
    2.0.10c: Track time between key presses and mistakes
    2.0.10d: Record more accurate intervals for each key
    2.0.11: Gamepad tracking
    2.0.12: Change resolutions to major keys
    2.0.13: Record history of tracks for animation
    """

    #Make sure version is in history, otherwise set to lowest version
    current_version_id = _get_id(data.get('Version', '-1'))
    current_time = time.time()
        
    if current_version_id < _get_id('2.0'):
        data['Count'] = 0
        data['Tracks'] = {}
        data['Clicks'] = {}
        data['Keys'] = {}
        data['Ticks'] = 0
        data['LastSave'] = current_time
        data['TimesLoaded'] = 0
        data['Version'] = '2.0'
        
    if current_version_id < _get_id('2.0.1'):
        data['Acceleration'] = {}
        
    if current_version_id < _get_id('2.0.1b'):
        del data['Acceleration']
        data['Speed'] = {}
        
    if current_version_id < _get_id('2.0.2'):
        data['Combined'] = {}
        
    if current_version_id < _get_id('2.0.3'):
        if update_metadata:
            data['Clicks'] = {}
        else:
            for resolution in data['Clicks']:
                data['Clicks'][resolution] = [data['Clicks'][resolution], {}, {}]
        data['Keys'] = {'Pressed': {}, 'Held': {}}
        data['Ticks'] = {'Current': data['Count'],
                         'Total': data['Ticks'],
                         'Recorded': data['Count']}
        del data['Count']
        
    if current_version_id < _get_id('2.0.4'):
        data['Time'] = {'Created': data['LastSave'],
                        'Modified': data['LastSave']}
        del data['LastSave']
        
    if current_version_id < _get_id('2.0.5'):
        data['Maps'] = {'Tracks': data['Tracks'], 'Clicks': data['Clicks'],
                        'Speed': data['Speed'], 'Combined': data['Combined'],
                        'Temp1': {}, 'Temp2': {}, 'Temp3': {}, 'Temp4': {},
                        'Temp5': {}, 'Temp6': {}, 'Temp7': {}, 'Temp8': {}}
        del data['Tracks']
        del data['Clicks']
        del data['Speed']
        del data['Combined']
        
    if current_version_id < _get_id('2.0.5b'):
        data['Ticks']['Current'] = {'Tracks': data['Ticks']['Current'],
                                    'Speed': data['Ticks']['Current']}
                                    
    if current_version_id < _get_id('2.0.6'):
        del data['Maps']['Speed']
        del data['Maps']['Combined']
        del data['Ticks']['Current']['Speed']
        
    if current_version_id < _get_id('2.0.6b'):
        data['Ticks']['Session'] = {'Current': data['Ticks']['Current']['Tracks'],
                                    'Total': data['Ticks']['Total']}
                                    
    if current_version_id < _get_id('2.0.6c'):
        data['Keys'] = {'All': data['Keys'], 'Session': {'Pressed': {}, 'Held': {}}}
        
    if current_version_id < _get_id('2.0.7'):
        changes = {'UNDERSCORE': 'HYPHEN',
                   'MULTIPLY': 'ASTERISK',
                   'AT': 'APOSTROPHE',
                   'HASH': 'NUMBER'}
        for old, new in get_items(changes):
            try:
                data['Keys']['All']['Pressed'][new] = data['Keys']['All']['Pressed'].pop(old)
                data['Keys']['All']['Held'][new] = data['Keys']['All']['Held'].pop(old)
            except KeyError:
                pass
            try:
                data['Keys']['Session']['Pressed'][new] = data['Keys']['Session']['Pressed'].pop(old)
                data['Keys']['Session']['Held'][new] = data['Keys']['Session']['Held'].pop(old)
            except KeyError:
                pass
                
    if current_version_id < _get_id('2.0.8'):
        data['SessionStarts'] = []
        
    if current_version_id < _get_id('2.0.9'):
        for resolution in data['Maps']['Tracks']:
            for k in data['Maps']['Tracks'][resolution].keys():
                if not 0 < k[0] < resolution[0] or not 0 < k[1] < resolution[1]:
                    del data['Maps']['Tracks'][resolution][k]
                    
    if current_version_id < _get_id('2.0.9b'):
        data['Ticks']['Tracks'] = int(data['Ticks']['Current']['Tracks'])
        data['Ticks']['Session']['Tracks'] = int(data['Ticks']['Session']['Current'])
        del data['Ticks']['Current']
        del data['Ticks']['Session']['Current']
        for resolution in data['Maps']['Tracks']:
            for k in data['Maps']['Tracks'][resolution]:
                if isinstance(data['Maps']['Tracks'][resolution][k], float):
                    data['Maps']['Tracks'][resolution][k] = int(data['Maps']['Tracks'][resolution][k])
                    
    if current_version_id < _get_id('2.0.9c'):
        data['Maps']['Session'] = {'Clicks': {}}
        
    if current_version_id < _get_id('2.0.9d'):
        del data['Maps']['Temp1']
        del data['Maps']['Temp2']
        del data['Maps']['Temp3']
        del data['Maps']['Temp4']
        del data['Maps']['Temp5']
        del data['Maps']['Temp6']
        del data['Maps']['Temp7']
        del data['Maps']['Temp8']
        data['Maps']['DoubleClicks'] = {}
        data['Maps']['Session']['DoubleClicks'] = {}
        
    if current_version_id < _get_id('2.0.9e'):
    
        def _test_resolution(aspects, x, y):
            for ax, ay in aspects:
                dx = x / ax
                if not dx % 1 and dx * ay == y:
                    return True
            return False
            
        aspects = [
            (4, 3),
            (16, 9),
            (16, 10),
            (18, 9),
            (21, 9),
        ]
        
        #Reverse and check for multi monitor setups
        aspects += [(y, x) for x, y in aspects]
        aspects += [(x * 2, y) for x, y in aspects] + [(x * 3, y) for x, y in aspects] + [(x * 5, y) for x, y in aspects]
        
        maps = ('Tracks', 'Clicks', 'DoubleClicks')
        for map in maps:
            for resolution in data['Maps'][map].keys():
                if not _test_resolution(aspects, *resolution):
                    del data['Maps'][map][resolution]
                    
    if current_version_id < _get_id('2.0.10'):
                        
        for maps in (data['Maps'], data['Maps']['Session']):
            maps['Click'] = {'Single': {'Left': {}, 'Middle': {}, 'Right': {}},
                             'Double': {'Left': {}, 'Middle': {}, 'Right': {}}}
            for resolution in maps['Clicks']:
                maps['Click']['Single']['Left'][resolution] = maps['Clicks'][resolution][0]
                maps['Click']['Single']['Middle'][resolution] = maps['Clicks'][resolution][1]
                maps['Click']['Single']['Right'][resolution] = maps['Clicks'][resolution][2]
            del maps['Clicks']
            for resolution in maps['DoubleClicks']:
                maps['Click']['Double']['Left'][resolution] = maps['DoubleClicks'][resolution][0]
                maps['Click']['Double']['Middle'][resolution] = maps['DoubleClicks'][resolution][1]
                maps['Click']['Double']['Right'][resolution] = maps['DoubleClicks'][resolution][2]
            del maps['DoubleClicks']
        
        IterateMaps(data['Maps']).convert()
        
    if current_version_id < _get_id('2.0.10b'):
        data['Maps']['Click']['Double'] = {'Left': {}, 'Middle': {}, 'Right': {}}
                    
    if current_version_id < _get_id('2.0.10c'):
        data['Keys']['All']['Intervals'] = {}
        data['Keys']['Session']['Intervals'] = {}
        data['Keys']['All']['Mistakes'] = {}
        data['Keys']['Session']['Mistakes'] = {}
                    
    if current_version_id < _get_id('2.0.10d'):
        data['Keys']['All']['Intervals'] = {'Total': data['Keys']['All']['Intervals'], 'Individual': {}}
        data['Keys']['Session']['Intervals'] = {'Total': data['Keys']['Session']['Intervals'], 'Individual': {}}

    if current_version_id < _get_id('2.0.11'):
        data['Gamepad'] = {'All': {'Buttons': {'Pressed': {}, 'Held': {}}, 'Axis': {}}}
    
    if current_version_id < _get_id('2.0.12'):
        data['Resolution'] = {}
        resolutions = data['Maps']['Tracks'].keys()
        for resolution in resolutions:
            data['Resolution'][resolution] = {}
            data['Resolution'][resolution]['Tracks'] = data['Maps']['Tracks'].pop(resolution)
            data['Resolution'][resolution]['Clicks'] = {}
            try:
                click_s_l = data['Maps']['Click']['Single']['Left'].pop(resolution)
            except KeyError:
                click_s_l = numpy.array(resolution, create=True)
            try:
                click_s_m = data['Maps']['Click']['Single']['Middle'].pop(resolution)
            except KeyError:
                click_s_m = numpy.array(resolution, create=True)
            try:
                click_s_r = data['Maps']['Click']['Single']['Right'].pop(resolution)
            except KeyError:
                click_s_r = numpy.array(resolution, create=True)
            try:
                click_d_l = data['Maps']['Click']['Double']['Left'].pop(resolution)
            except KeyError:
                click_d_l = numpy.array(resolution, create=True)
            try:
                click_d_m = data['Maps']['Click']['Double']['Middle'].pop(resolution)
            except KeyError:
                click_d_m = numpy.array(resolution, create=True)
            try:
                click_d_r = data['Maps']['Click']['Double']['Right'].pop(resolution)
            except KeyError:
                click_d_r = numpy.array(resolution, create=True)
            clicks = {'Single': {'Left': click_s_l,
                                 'Middle': click_s_m,
                                 'Right': click_s_r},
                      'Double': {'Left': click_d_l,
                                 'Middle': click_d_m,
                                 'Right': click_d_r}}
            data['Resolution'][resolution]['Clicks']['All'] = clicks
            
        del data['Maps']
    
    if current_version_id < _get_id('2.0.13'):
        data['HistoryAnimation'] = {'Tracks': [], 'Clicks': [], 'Keyboard': []}
    
    if update_metadata:     
    
        #Only count as new session if updated or last save was over an hour ago
        if (data.get('Version', '-1') != VERSION or not data['SessionStarts'] or current_time - 3600 > data['Time']['Modified']):
            data['Ticks']['Session']['Tracks'] = data['Ticks']['Tracks']
            data['Ticks']['Session']['Total'] = data['Ticks']['Total']
            data['Keys']['Session']['Pressed'] = {}
            data['Keys']['Session']['Held'] = {}
            data['Keys']['Session']['Intervals'] = {'Total': {}, 'Individual': {}}
            data['Keys']['Session']['Mistakes'] = {}
            
            #Empty session arrays
            for resolution, values in get_items(data['Resolution']):
                if 'Session' not in values['Clicks']:
                    values['Clicks']['Session'] = {'Single': {'Left': numpy.array(resolution, create=True),
                                                              'Middle': numpy.array(resolution, create=True),
                                                              'Right': numpy.array(resolution, create=True)},
                                                   'Double': {'Left': numpy.array(resolution, create=True),
                                                              'Middle': numpy.array(resolution, create=True),
                                                              'Right': numpy.array(resolution, create=True)}}
                else:
                    try:
                        values['Clicks']['Session']['Single']['Left'] = numpy.fill(values['Clicks']['Session']['Single']['Left'], 0)
                    except AttributeError:
                        values['Clicks']['Session']['Single']['Left'] = numpy.array(resolution, create=True)
                    try:
                        values['Clicks']['Session']['Single']['Middle'] = numpy.fill(values['Clicks']['Session']['Single']['Middle'], 0)
                    except AttributeError:
                        values['Clicks']['Session']['Single']['Middle'] = numpy.array(resolution, create=True)
                    try:
                        values['Clicks']['Session']['Single']['Right'] = numpy.fill(values['Clicks']['Session']['Single']['Right'], 0)
                    except AttributeError:
                        values['Clicks']['Session']['Single']['Right'] = numpy.array(resolution, create=True)
                    try:
                        values['Clicks']['Session']['Double']['Left'] = numpy.fill(values['Clicks']['Session']['Double']['Left'], 0)
                    except AttributeError:
                        values['Clicks']['Session']['Double']['Left'] = numpy.array(resolution, create=True)
                    try:
                        values['Clicks']['Session']['Double']['Middle'] = numpy.fill(values['Clicks']['Session']['Double']['Middle'], 0)
                    except AttributeError:
                        values['Clicks']['Session']['Double']['Middle'] = numpy.array(resolution, create=True)
                    try:
                        values['Clicks']['Session']['Double']['Right'] = numpy.fill(values['Clicks']['Session']['Double']['Right'], 0)
                    except AttributeError:
                        values['Clicks']['Session']['Double']['Right'] = numpy.array(resolution, create=True)
                        
            data['Gamepad']['Session'] = {'Buttons': {'Pressed': {}, 'Held': {}}, 'Axis': {}}
            data['TimesLoaded'] += 1
            data['SessionStarts'].append(current_time)
            
        data['Version'] = VERSION
        
    return data