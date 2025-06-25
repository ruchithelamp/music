from src.spotify_loader import SpotifyLoader

loader = SpotifyLoader()

tracks = loader.search_tracks("Blinding Lights")
# for track in tracks:
#     print(track)

print(tracks[0])
track_id = '1Xyo4u8uXC1ZmMpatF05PJ' # = tracks[0]['id']
features = loader.get_track_features(track_id)
print(f"\nAudio Features for '{tracks[0]['name']}':")
print(features)




# {'album': 
#  {'album_type': 'album', 'artists': 
#   [{'external_urls': 
#     {'spotify': 'https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ'}, 
#     'href': 'https://api.spotify.com/v1/artists/1Xyo4u8uXC1ZmMpatF05PJ', 
#     'id': '1Xyo4u8uXC1ZmMpatF05PJ', 
#     'name': 'The Weeknd', 'type': 'artist', 
#     'uri': 'spotify:artist:1Xyo4u8uXC1ZmMpatF05PJ'}], 
#     'available_markets': ['AR', 'AU', 'AT', 'BE', 'BO', 'BR', 'BG', 'CA', 'CL', 'CO', 'CR', 'CY', 'CZ', 'DK', 'DO', 'DE', 'EC', 'EE', 'SV', 'FI', 'FR', 'GR', 'GT', 'HN', 'HK', 'HU', 'IS', 'IE', 'IT', 'LV', 'LT', 'LU', 'MY', 'MT', 'MX', 'NL', 'NZ', 'NI', 'NO', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'SG', 'SK', 'ES', 'SE', 'CH', 'TW', 'TR', 'UY', 'US', 'GB', 'AD', 'LI', 'MC', 'ID', 'JP', 'TH', 'VN', 'RO', 'IL', 'ZA', 'SA', 'AE', 'BH', 'QA', 'OM', 'KW', 'EG', 'MA', 'DZ', 'TN', 'LB', 'JO', 'PS', 'IN', 'BY', 'KZ', 'MD', 'UA', 'AL', 'BA', 'HR', 'ME', 'MK', 'RS', 'SI', 'KR', 'BD', 'PK', 'LK', 'GH', 'KE', 'NG', 'TZ', 'UG', 'AG', 'AM', 'BS', 'BB', 'BZ', 'BT', 'BW', 'BF', 'CV', 'CW', 'DM', 'FJ', 'GM', 'GE', 'GD', 'GW', 'GY', 'HT', 'JM', 'KI', 'LS', 'LR', 'MW', 'MV', 'ML', 'MH', 'FM', 'NA', 'NR', 'NE', 'PW', 'PG', 'WS', 'SM', 'ST', 'SN', 'SC', 'SL', 'SB', 'KN', 'LC', 'VC', 'SR', 'TL', 'TO', 'TT', 'TV', 'VU', 'AZ', 'BN', 'BI', 'KH', 'CM', 'TD', 'KM', 'GQ', 'SZ', 'GA', 'GN', 'KG', 'LA', 'MO', 'MR', 'MN', 'NP', 'RW', 'TG', 'UZ', 'ZW', 'BJ', 'MG', 'MU', 'MZ', 'AO', 'CI', 'DJ', 'ZM', 'CD', 'CG', 'IQ', 'LY', 'TJ', 'VE', 'ET', 'XK'], 'external_urls': {'spotify': 'https://open.spotify.com/album/4yP0hdKOZPNshxUOjY0cZj'}, 'href': 'https://api.spotify.com/v1/albums/4yP0hdKOZPNshxUOjY0cZj', 'id': '4yP0hdKOZPNshxUOjY0cZj', 'images': [{'height': 640, 'width': 640, 'url': 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36'}, {'height': 300, 'width': 300, 'url': 'https://i.scdn.co/image/ab67616d00001e028863bc11d2aa12b54f5aeb36'}, {'height': 64, 'width': 64, 'url': 'https://i.scdn.co/image/ab67616d000048518863bc11d2aa12b54f5aeb36'}], 'is_playable': True, 'name': 'After Hours', 'release_date': '2020-03-20', 'release_date_precision': 'day', 'total_tracks': 14, 'type': 'album', 'uri': 'spotify:album:4yP0hdKOZPNshxUOjY0cZj'}, 'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ'}, 'href': 'https://api.spotify.com/v1/artists/1Xyo4u8uXC1ZmMpatF05PJ', 'id': '1Xyo4u8uXC1ZmMpatF05PJ', 'name': 'The Weeknd', 'type': 'artist', 'uri': 'spotify:artist:1Xyo4u8uXC1ZmMpatF05PJ'}], 'available_markets': ['AR', 'AU', 'AT', 'BE', 'BO', 'BR', 'BG', 'CA', 'CL', 'CO', 'CR', 'CY', 'CZ', 'DK', 'DO', 'DE', 'EC', 'EE', 'SV', 'FI', 'FR', 'GR', 'GT', 'HN', 'HK', 'HU', 'IS', 'IE', 'IT', 'LV', 'LT', 'LU', 'MY', 'MT', 'MX', 'NL', 'NZ', 'NI', 'NO', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'SG', 'SK', 'ES', 'SE', 'CH', 'TW', 'TR', 'UY', 'US', 'GB', 'AD', 'LI', 'MC', 'ID', 'JP', 'TH', 'VN', 'RO', 'IL', 'ZA', 'SA', 'AE', 'BH', 'QA', 'OM', 'KW', 'EG', 'MA', 'DZ', 'TN', 'LB', 'JO', 'PS', 'IN', 'BY', 'KZ', 'MD', 'UA', 'AL', 'BA', 'HR', 'ME', 'MK', 'RS', 'SI', 'KR', 'BD', 'PK', 'LK', 'GH', 'KE', 'NG', 'TZ', 'UG', 'AG', 'AM', 'BS', 'BB', 'BZ', 'BT', 'BW', 'BF', 'CV', 'CW', 'DM', 'FJ', 'GM', 'GE', 'GD', 'GW', 'GY', 'HT', 'JM', 'KI', 'LS', 'LR', 'MW', 'MV', 'ML', 'MH', 'FM', 'NA', 'NR', 'NE', 'PW', 'PG', 'WS', 'SM', 'ST', 'SN', 'SC', 'SL', 'SB', 'KN', 'LC', 'VC', 'SR', 'TL', 'TO', 'TT', 'TV', 'VU', 'AZ', 'BN', 'BI', 'KH', 'CM', 'TD', 'KM', 'GQ', 'SZ', 'GA', 'GN', 'KG', 'LA', 'MO', 'MR', 'MN', 'NP', 'RW', 'TG', 'UZ', 'ZW', 'BJ', 'MG', 'MU', 'MZ', 'AO', 'CI', 'DJ', 'ZM', 'CD', 'CG', 'IQ', 'LY', 'TJ', 'VE', 'ET', 'XK'], 'disc_number': 1, 'duration_ms': 200040, 'explicit': False, 'external_ids': {'isrc': 'USUG11904206'}, 'external_urls': {'spotify': 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b'}, 'href': 'https://api.spotify.com/v1/tracks/0VjIjW4GlUZAMYd2vXMi3b', 'id': '0VjIjW4GlUZAMYd2vXMi3b', 'is_local': False, 'is_playable': True, 'name': 'Blinding Lights', 'popularity': 89, 'preview_url': None, 'track_number': 9, 'type': 'track', 'uri': 'spotify:track:0VjIjW4GlUZAMYd2vXMi3b'}



