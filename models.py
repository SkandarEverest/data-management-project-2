from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

# Enums
JenjangEnum = Literal['S1', 'S2', 'S3', 'Profesi']
StatusPernikahanEnum = Literal['Belum Menikah','Menikah','Cerai Hidup','Cerai Mati']
TipeAlamatEnum = Literal['selama kuliah','tetap','penanggung jawab','darurat']
HubunganEnum = Literal['Ayah','Ibu','Wali','Lainnya']
NilaiHurufEnum = Literal['A','AB','B','BC','C','D','E','F','T','P']

class Fakultas(BaseModel):
    kodeFakultas: str
    namaFakultas: str

class ProgramStudi(BaseModel):
    kodeProdi: str
    namaProdi: str
    jenjang: JenjangEnum
    kodeFakultas: str
    kaprodiNip: Optional[str] = None
    statusAkreditasi: str

class Dosen(BaseModel):
    nip: str
    namaDosen: str
    email: Optional[str] = None
    kodeFakultas: str
    kelompokKeahlian: Optional[str] = None
    jabatanFungsional: Optional[str] = None
    usernames: list[str] | None = None 

# ---------- Subdocs untuk Mahasiswa ----------

class Biodata(BaseModel):
    pasFoto: Optional[str] = None
    namaDiDokumenKuliah: Optional[str] = None
    jenisKelamin: Optional[Literal['L','P']] = None
    tanggalLahir: Optional[datetime] = None
    negaraKelahiran: Optional[str] = None
    statusPernikahan: Optional[StatusPernikahanEnum] = None
    wargaNegara: Optional[str] = None
    nik: Optional[str] = None
    agama: Optional[str] = None
    anakKe: Optional[int] = None
    jumlahAnak: Optional[int] = None
    penyediaAsuransiKesehatan: Optional[str] = None
    nomorKartuAsuransiKesehatan: Optional[str] = None
    jenisAsuransiKesehatan: Optional[str] = None
    masaBerlakuAsuransiKesehatan: Optional[datetime] = None

class Alamat(BaseModel):
    tipeAlamat: TipeAlamatEnum
    alamat: Optional[str] = None
    kodePos: Optional[str] = None
    kodeKota: Optional[str] = None
    negara: Optional[str] = None
    noKontak: Optional[str] = None
    namaKota: Optional[str] = None
    email: Optional[str] = None
    noHandphone: Optional[str] = None

class OrangTua(BaseModel):
    nama: str
    hubungan: HubunganEnum
    penghasilanKotor: Optional[float] = None
    pekerjaan: Optional[str] = None
    instansiBekerja: Optional[str] = None
    pendidikan: Optional[str] = None
    tanggalLahir: Optional[datetime] = None
    statusKehidupan: Optional[str] = None       # misal: 'Hidup' / 'Meninggal'

class StatusKeuangan(BaseModel):
    semester: int
    tagihan: float
    pembayaran: float
    batasPembayaran: Optional[datetime] = None

class TugasAkhir(BaseModel):
    judulBahasaInggris: Optional[str] = None
    judulBahasaIndonesia: str
    dosenPembimbing1: str
    dosenPembimbing2: Optional[str] = None

class Alumni(BaseModel):
    nomorIjazah: str
    tanggalLulus: Optional[datetime] = None
    gelar: Optional[str] = None
    predikat: Optional[str] = None

class Mahasiswa(BaseModel):
    nim: str
    namaLengkap: str
    kelas: Optional[str] = None
    tahunMasuk: int
    kodeFakultas: str
    kodeProdi: str
    noRegistrasi: Optional[str] = None
    username: Optional[str] = None
    dosenWali: Optional[str] = None

    biodata: Optional[Biodata] = None
    alamat: List[Alamat] = []
    orangTua: List[OrangTua] = []
    statusKeuangan: List[StatusKeuangan] = []
    tugasAkhir: Optional[TugasAkhir] = None
    alumni: Optional[Alumni] = None

class MataKuliahRS(BaseModel):
    kodeProdi: str
    tahun: int
    kodeMatkul: str
    disetujui: bool
    nilai: Optional[str] = None

class RencanaStudi(BaseModel):
    nim: str
    tahunAjaran: str
    semester: int

    pengirimanRencanaStudi: Optional[datetime] = None
    persetujuanDosenWali: Optional[datetime] = None
    pembayaranUkt: bool = False
    pengesahanKsm: Optional[datetime] = None
    pengirimanRencanaStudiPrs: Optional[datetime] = None
    persetujuanDosenWaliPrs: Optional[datetime] = None
    pengesahanKsmPengganti: Optional[datetime] = None

    maksimalBeban: Optional[int] = None
    mataKuliah: List[MataKuliahRS]

