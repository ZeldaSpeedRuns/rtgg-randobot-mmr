import json
import requests

class ZSR:
    """
    Class for interacting with mmrandomizer.com to generate seeds and available presets.
    """
    seed_public = 'https://mmrandomizer.com/seed/get?id=%(id)s'
    seed_endpoint = 'https://mmrandomizer.com/api/v2/seed/create'
    status_endpoint = 'https://mmrandomizer.com/api/v2/seed/status'
    details_endpoint = 'https://mmrandomizer.com/api/v2/seed/details'
    version_endpoint = 'https://mmrandomizer.com/api/version'
    settings_endpoint = 'https://raw.githubusercontent.com/ZoeyZolotova/mm-rando/refs/heads/master/MMR.Web.Config/presets_default.json'
    settings_dev_endpoint = 'https://raw.githubusercontent.com/ZoeyZolotova/mm-rando/refs/heads/dev/MMR.Web.Config/presets_default.json'

    hash_map = {
        'Beans': 'HashBeans',
        'Big Magic': 'HashBigMagic',
        'Bombchu': 'HashBombchu',
        'Boomerang': 'HashBoomerang',
        'Boss Key': 'HashBossKey',
        'Bottled Fish': 'HashBottledFish',
        'Bottled Milk': 'HashBottledMilk',
        'Bow': 'HashBow',
        'Compass': 'HashCompass',
        'Cucco': 'HashCucco',
        'Deku Nut': 'HashDekuNut',
        'Deku Stick': 'HashDekuStick',
        'Fairy Ocarina': 'HashFairyOcarina',
        'Frog': 'HashFrog',
        'Gold Scale': 'HashGoldScale',
        'Heart Container': 'HashHeart',
        'Hover Boots': 'HashHoverBoots',
        'Kokiri Tunic': 'HashKokiriTunic',
        'Lens of Truth': 'HashLensOfTruth',
        'Longshot': 'HashLongshot',
        'Map': 'HashMap',
        'Mask of Truth': 'HashMaskOfTruth',
        'Master Sword': 'HashMasterSword',
        'Megaton Hammer': 'HashHammer',
        'Mirror Shield': 'HashMirrorShield',
        'Mushroom': 'HashMushroom',
        'Saw': 'HashSaw',
        'Silver Gauntlets': 'HashSilvers',
        'Skull Token': 'HashSkullToken',
        'Slingshot': 'HashSlingshot',
        'SOLD OUT': 'HashSoldOut',
        'Stone of Agony': 'HashStoneOfAgony',
    }

    def __init__(self, mmr_api_key):
        self.mmr_api_key = mmr_api_key
        self.presets = self.load_presets()
        self.presets_dev = self.load_presets(dev=True)
        self.last_known_dev_version = None
        self.get_latest_dev_version()

    def load_presets(self, dev=False):
        """
        Load and return available seed presets.
        """
        if dev:
            settings = requests.get(self.settings_dev_endpoint).json()
        else:
            settings = requests.get(self.settings_endpoint).json()

        return {
            min(settings[preset]['aliases'], key=len): {
                'full_name': preset,
                'settings': settings.get(preset),
            }
            for preset in settings
        }

    def get_latest_dev_version(self):
        """
        Returns currently active dev version and a bool indicating if it's changed.
        """
        version_req = requests.get(self.version_endpoint, params={'branch': 'dev'}).json()
        latest_dev_version = version_req['currentlyActiveVersion']
        if latest_dev_version != self.last_known_dev_version:
            self.last_known_dev_version = latest_dev_version
            return latest_dev_version, True
        return latest_dev_version, False

    def roll_seed(self, preset, encrypt, dev):
        """
        Generate a seed and return its public URL.
        """
        if dev:
            latest_dev_version, changed = self.get_latest_dev_version()
            if changed:
                self.presets_dev = self.load_presets(dev=True)
            req_body = json.dumps(self.presets_dev[preset]['settings'])
        else:
            req_body = json.dumps(self.presets[preset]['settings'])

        params = {
            'key': self.mmr_api_key,
        }
        if encrypt and not dev:
            params['encrypt'] = 'true'
        if encrypt and dev:
            params['locked'] = 'true'
        if dev:
            params['version'] = 'dev_' + latest_dev_version
        data = requests.post(self.seed_endpoint, req_body, params=params,
                             headers={'Content-Type': 'application/json'}).json()
        return data['id'], self.seed_public % data

    def get_status(self, seed_id):
        data = requests.get(self.status_endpoint, params={
            'id': seed_id,
            'key': self.mmr_api_key,
        }).json()
        return data['status']

    def get_hash(self, seed_id):
        data = requests.get(self.details_endpoint, params={
            'id': seed_id,
            'key': self.mmr_api_key,
        }).json()
        try:
            settings = json.loads(data.get('settingsLog'))
        except ValueError:
            return None
        return ' '.join(
            self.hash_map.get(item, item)
            for item in settings['file_hash']
        )
