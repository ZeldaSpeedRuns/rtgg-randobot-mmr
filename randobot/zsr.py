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

    valid_versions = (
        ('stable', '2.0 RC', 'master', 'https://raw.githubusercontent.com/ZoeyZolotova/mm-rando/refs/heads/dev/MMR.Web.Config/presets_default.json'),
    )

    hash_map = {
        "ITEM_OCARINA": "HashOcarina",
        "ITEM_BOW": "HashBow",
        "ITEM_FIRE_ARROW": "HashFireArrow",
        "ITEM_ICE_ARROW": "HashIceArrow",
        "ITEM_LIGHT_ARROW": "HashLightArrow",
        "ITEM_BOMB": "HashBomb",
        "ITEM_BOMBCHU": "HashBombchu",
        "ITEM_DEKU_STICK": "HashDekuStick",
        "ITEM_DEKU_NUT": "HashDekuNut",
        "ITEM_MAGIC_BEAN": "HashBean",
        "ITEM_POWDER_KEG": "HashPowderKeg",
        "ITEM_PICTOGRAPH": "HashPictograph",
        "ITEM_LENS": "HashLens",
        "ITEM_HOOKSHOT": "HashHookshot",
        "ITEM_EMPTY_BOTTLE": "HashEmptyBottle",
        "ITEM_DEKU_PRINCESS": "HashDekuPrincess",
        "ITEM_BUGS": "HashBugs",
        "ITEM_BIG_POE": "HashBigPoe",
        "ITEM_HOT_WATER": "HashHotWater",
        "ITEM_ZORA_EGG": "HashZoraEgg",
        "ITEM_GOLD_DUST_BOTTLE": "HashGoldDust",
        "ITEM_MUSHROOM": "HashMushroom",
        "ITEM_SEAHORSE": "HashSeahorse",
        "ITEM_CHATEAU_ROMANI_BOTTLE": "HashChateau",
        "ITEM_MOON_TEAR": "HashMoonsTear",
        "ITEM_TOWN_DEED": "HashLandDeed",
        "ITEM_ROOM_KEY": "HashRoomKey",
        "ITEM_MAMA_LETTER": "HashMamaLetter",
        "ITEM_KAFEI_LETTER": "HashKafeiLetter",
        "ITEM_PENDANT": "HashPendant",
        "ITEM_MAP": "HashMap",
        "ITEM_DEKU_MASK": "HashDekuMask",
        "ITEM_GORON_MASK": "HashGoronMask",
        "ITEM_ZORA_MASK": "HashZoraMask",
        "ITEM_FIERCE_DEITY_MASK": "HashFierceDeity",
        "ITEM_MASK_OF_TRUTH": "HashMaskOfTruth",
        "ITEM_KAFEI_MASK": "HashKafeiMask",
        "ITEM_ALL_NIGHT_MASK": "HashAllNightMask",
        "ITEM_BUNNY_HOOD": "HashBunnyHood",
        "ITEM_KEATON_MASK": "HashKeatonMask",
        "ITEM_GARO_MASK": "HashGaroMask",
        "ITEM_ROMANI_MASK": "HashRomaniMask",
        "ITEM_CIRCUS_LEADER_MASK": "HashCircusLeader",
        "ITEM_POSTMAN_HAT": "HashPostmansHat",
        "ITEM_COUPLE_MASK": "HashCouplesMask",
        "ITEM_FAIRY_SWORD": "HashGFS",
        "ITEM_GIBDO_MASK": "HashGibdoMask",
        "ITEM_DON_GERO_MASK": "HashDonGeroMask",
        "ITEM_KAMARO_MASK": "HashKamaroMask",
        "ITEM_CAPTAIN_HAT": "HashCaptainsHat",
        "ITEM_STONE_MASK": "HashStoneMask",
        "ITEM_BREMEN_MASK": "HashBremenMask",
        "ITEM_BLAST_MASK": "HashBlastMask",
        "ITEM_MASK_OF_SCENTS": "HashMaskOfScents",
        "ITEM_GIANT_MASK": "HashGiantsMask",
        "ITEM_KOKIRI_SWORD": "HashKokiriSword",
        "ITEM_GILDED_SWORD": "HashGildedSword",
        "ITEM_HELIX_SWORD": "HashHelixSword",
        "ITEM_HERO_SHIELD": "HashHeroShield",
        "ITEM_MIRROR_SHIELD": "HashMirrorShield",
        "ITEM_QUIVER_40": "HashQuiver",
        "ITEM_ADULT_WALLET": "HashAdultWallet",
        "ITEM_BOMBERS_NOTEBOOK": "HashBombersNote",
        "0x61": "HashBombersNote"
    }

    def __init__(self, mmr_api_key):
        self.mmr_api_key = mmr_api_key
        self.version_map = {}
        self.build_version_map()

    def build_version_map(self):
        for i in range(len(self.valid_versions)):
            self.version_map[self.valid_versions[i][0]] = Branch(
                rtgg_arg=self.valid_versions[i][0],
                name=self.valid_versions[i][1],
                mmr_name=self.valid_versions[i][2],
                settings_endpoint=self.valid_versions[i][3]
            )

    def roll_seed(self, preset, branch, encrypt):
        """
        Generate a seed and return its public URL.
        """
        dev = branch.rtgg_arg != 'stable'

        if dev:
            latest_version = branch.get_latest_version()
            if latest_version != branch.version:
                branch.update_version(latest_version)
                branch.load_presets()
        req_body = json.dumps(branch.presets[preset]['settings'])

        params = {
            'key': self.mmr_api_key,
        }
        if encrypt and not dev:
            params['encrypt'] = 'true'
        if encrypt and dev:
            params['locked'] = 'true'
        if dev:
            params['version'] = branch.mmr_name + '_' + branch.version

        try:
            response = requests.post(self.seed_endpoint, req_body, params=params,
                                   headers={'Content-Type': 'application/json'}, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['id'], self.seed_public % data
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError, KeyError) as e:
            raise RuntimeError(f"Failed to create seed: {e}")

    def get_status(self, seed_id):
        try:
            response = requests.get(self.status_endpoint, params={
                'id': seed_id,
                'key': self.mmr_api_key,
            }, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['status']
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError, KeyError) as e:
            raise RuntimeError(f"Failed to get seed status for ID '{seed_id}': {e}")

    def get_hash(self, seed_id):
        try:
            response = requests.get(self.details_endpoint, params={
                'id': seed_id,
                'key': self.mmr_api_key,
            }, timeout=10)
            response.raise_for_status()
            data = response.json()

            try:
                settings = json.loads(data.get('settingsLog'))
            except (ValueError, TypeError):
                return None

            return ' '.join(
                self.hash_map.get(item, item)
                for item in settings['Hash']
            )
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to get seed hash for ID '{seed_id}': {e}")

class Branch:
    def __init__(self, rtgg_arg, name, mmr_name, settings_endpoint):
        self.rtgg_arg = rtgg_arg
        self.name = name
        self.mmr_name = mmr_name
        self.settings_endpoint = settings_endpoint
        self.version = self.get_latest_version()
        self.presets = self.load_presets()

    def load_presets(self):
        try:
            response = requests.get(self.settings_endpoint, timeout=10)
            response.raise_for_status()
            settings = response.json()

            return {
                preset: {
                    'full_name': preset,
                    'settings': settings[preset],
                }
                for preset in settings
            }
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load presets from '{self.settings_endpoint}': {e}")
    
    def get_latest_version(self):
        """
        Fetch the latest version of the supplied randomizer branch.
        """
        try:
            response = requests.get(ZSR.version_endpoint, params={'branch': self.mmr_name}, timeout=10)
            response.raise_for_status()
            version_req = response.json()
            latest_version = version_req['currentlyActiveVersion']
            return latest_version
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError, KeyError) as e:
            raise RuntimeError(f"Failed to fetch version for branch '{self.mmr_name}': {e}")
    
    def update_version(self, version):
        self.version = version
