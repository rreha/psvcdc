from __future__ import absolute_import
from __future__ import print_function
from Crypto.Cipher import AES
from Crypto.Util import Counter
from scetypes import SecureBool, SceType, KeyType, SelfType, SceSegment, SelfHeader, AppInfoHeader, MetadataInfo, MetadataHeader, MetadataSection, SrvkHeader, SpkgHeader, CompressionType, EncryptionType
from six.moves import range

def print_metadata_keyvault(keys):
    print(' Metadata Vault:')
    for i in range(len(keys)):
        print('  {0:#0{1}x}:      {2}'.format(i,4, keys[i].hex()))

def get_segments(inf, sce_hdr, sysver=-1, self_type=SelfType.NONE, keytype=0, klictxt=0, silent=False):
    from keys import SCE_KEYS
    inf.seek(sce_hdr.metadata_offset + 48)
    dat = inf.read(sce_hdr.header_length - sce_hdr.metadata_offset - 48)
    (key, iv) = SCE_KEYS.get(KeyType.METADATA, sce_hdr.sce_type, sysver, sce_hdr.key_revision, self_type)
    hdr_dec = AES.new(key, AES.MODE_CBC, iv)
    if self_type == SelfType.APP:
        keytype = 0
        if sce_hdr.key_revision >= 2:
            keytype=1
        (np_key, np_iv) = SCE_KEYS.get(KeyType.NPDRM, sce_hdr.sce_type, sysver, keytype, self_type)
        npdrm_dec = AES.new(np_key, AES.MODE_CBC, np_iv)
        #klickey = klictxt.hex()
        #print klictxt.hex()
        predec = npdrm_dec.decrypt(klictxt)
        #print predec.hex()
        npdrm_dec2 = AES.new(predec, AES.MODE_CBC, np_iv)
        dec_in = npdrm_dec2.decrypt(dat[0:MetadataInfo.Size])
    else:
        dec_in = dat[0:MetadataInfo.Size]
        
          
    dec = hdr_dec.decrypt(dec_in)
    metadata_info = MetadataInfo(dec)
    if not silent:
        print(metadata_info)
    contents_dec = AES.new(metadata_info.key, AES.MODE_CBC, metadata_info.iv)
    dec = contents_dec.decrypt(dat[MetadataInfo.Size:])
    metadata_hdr = MetadataHeader(dec[0:MetadataHeader.Size])
    if not silent:
        print(metadata_hdr)
    segs = {}
    start = MetadataHeader.Size + metadata_hdr.section_count * MetadataSection.Size
    vault = [dec[start + 16 * x:start + 16 * (x + 1)] for x in range(metadata_hdr.key_count)]
    if not silent:
        print_metadata_keyvault(vault)
    for i in range(metadata_hdr.section_count):
        metsec = MetadataSection(dec[MetadataHeader.Size + i*MetadataSection.Size:MetadataHeader.Size + i*MetadataSection.Size + MetadataSection.Size])
        if not silent:
            print(metsec)
        if metsec.encryption == EncryptionType.AES128CTR:
            segs[i] = SceSegment(metsec.offset, metsec.seg_idx, metsec.size, metsec.compression == CompressionType.DEFLATE, vault[metsec.key_idx], vault[metsec.iv_idx])
    return segs

def get_key_type(inf, sce_hdr, silent=False):
    if sce_hdr.sce_type == SceType.SELF:
        inf.seek(32)
        self_hdr = SelfHeader(inf.read(SelfHeader.Size))
        inf.seek(self_hdr.appinfo_offset)
        appinfo_hdr = AppInfoHeader(inf.read(AppInfoHeader.Size))
        if not silent:
            print(appinfo_hdr)
        return (appinfo_hdr.sys_version, appinfo_hdr.self_type)
    elif sce_hdr.sce_type == SceType.SRVK:
        inf.seek(sce_hdr.header_length)
        srvk = SrvkHeader(inf.read(SrvkHeader.Size))
        if not silent:
            print(srvk)
        return (srvk.sys_version, SelfType.NONE)
    elif sce_hdr.sce_type == SceType.SPKG:
        inf.seek(sce_hdr.header_length)
        spkg = SpkgHeader(inf.read(SpkgHeader.Size))
        if not silent:
            print(spkg)
        return (spkg.update_version << 16, SelfType.NONE)
    else:
        print('Unknown system version for type {}'.format(sce_hdr.sce_type))
        return -1
