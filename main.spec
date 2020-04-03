# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\kusta\\Documents\\PyRadio'],
             binaries=[],
             datas=[('dll-s/libvlc.dll', '.'),
                ('dll-s/axvlc.dll', '.'),
                ('dll-s/libvlccore.dll', '.'),
                ('dll-s/npvlc.dll', '.'),
                ('./radios.txt', '.'),
                ('./icon/pyradio.ico', './icon'),
                ('./css/main.css', './css')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += Tree('C:\Program Files\VideoLAN\VLC\plugins', prefix='plugins')
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='PyRadio',
          windowed=True,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
