from faker import Faker
import random
from datetime import datetime, timedelta
from db import get_db
from models import (
    Fakultas, ProgramStudi, Dosen, Mahasiswa,
    Biodata, Alamat, OrangTua, StatusKeuangan,
    TugasAkhir, Alumni,
)

fake = Faker("id_ID")  # locale Indonesia
db = get_db()

NUM_FAKULTAS = 13
NUM_PRODI = 140
NUM_DOSEN = 3540
NUM_MAHASISWA = 33296

TARGET_ALAMAT_PER_MHS = 2.5
TARGET_STATUS_PER_MHS = 4
TARGET_RS_PER_MHS = 4
TARGET_MK_PER_RS = 7
TARGET_KEHADIRAN_PER_PERTEMUAN = 33


def seed_fakultas(n=NUM_FAKULTAS):
    db.fakultas.delete_many({})

    fakultas_list = []
    for i in range(1, n + 1):
        kode = f"FK{i:02d}"  # FK01, FK02, ...
        nama = f"Fakultas {i}"
        fakultas_list.append(Fakultas(kodeFakultas=kode, namaFakultas=nama))

    docs = [f.model_dump() for f in fakultas_list]
    db.fakultas.insert_many(docs)
    print("Inserted fakultas:", len(docs))
    return docs


def seed_prodi(n=NUM_PRODI):
    db.program_studi.delete_many({})

    fakultas = list(db.fakultas.find({}))
    if not fakultas:
        raise RuntimeError("Fakultas must be seeded before program_studi")

    jenjang_choices = ["S1", "S2", "S3", "Profesi"]
    akreditasi_choices = ["Unggul", "A", "B", "C"]

    prodi_list = []
    for i in range(1, n + 1):
        fk = fakultas[(i - 1) % len(fakultas)]  # sebar rata ke semua fakultas
        kode_prodi = f"PR{i:03d}"               # PR001, PR002, ...
        nama_prodi = f"Program Studi {i}"

        prodi_list.append(ProgramStudi(
            kodeProdi=kode_prodi,
            namaProdi=nama_prodi,
            jenjang=random.choice(jenjang_choices),
            kodeFakultas=fk["kodeFakultas"],
            kaprodiNip=None,
            statusAkreditasi=random.choice(akreditasi_choices),
        ))

    docs = [p.model_dump() for p in prodi_list]
    db.program_studi.insert_many(docs)
    print("Inserted program_studi:", len(docs))
    return docs


def seed_dosen(n=NUM_DOSEN):
    db.dosen.delete_many({})

    fakultas = list(db.fakultas.find({}))
    if not fakultas:
        raise RuntimeError("Fakultas must be seeded before dosen")

    docs = []
    used_nip = set()

    for _ in range(n):
        # pastikan NIP unik
        while True:
            nip = f"{fake.random_number(digits=10):010d}"
            if nip not in used_nip:
                used_nip.add(nip)
                break

        fk = random.choice(fakultas)

        d = Dosen(
            nip=nip,
            namaDosen=fake.name(),
            email=fake.unique.email(),
            kodeFakultas=fk["kodeFakultas"],
            kelompokKeahlian=fake.job(),
            jabatanFungsional=random.choice(["Asisten Ahli","Lektor","Lektor Kepala","Guru Besar"]),
        )
        docs.append(d.model_dump())

    db.dosen.insert_many(docs)
    print("Inserted dosen:", len(docs))
    return docs


def random_biodata():
    dob = fake.date_of_birth(minimum_age=18, maximum_age=25)
    dob_dt = datetime.combine(dob, datetime.min.time())
    return Biodata(
        pasFoto=f"{fake.file_name(extension='jpg')}",
        namaDiDokumenKuliah=fake.name(),
        jenisKelamin=random.choice(['L','P']),
        tanggalLahir=dob_dt,
        negaraKelahiran="Indonesia",
        statusPernikahan=random.choice(['Belum Menikah','Menikah']),
        wargaNegara="Indonesia",
        nik=str(fake.random_number(digits=16)),
        agama=random.choice(["Islam","Kristen","Katolik","Hindu","Buddha","Konghucu"]),
    )

def random_alamat():
    # 2 atau 3 alamat per mahasiswa
    add_third = random.random() < 0.5  # 50% dapat alamat ke-3 → rata2 ≈ 2.5

    base = [
        Alamat(
            tipeAlamat="selama kuliah",
            alamat=fake.street_address(),
            kodePos=fake.postcode(),
            kodeKota="BDG",
            negara="Indonesia",
            noKontak=fake.phone_number(),
            namaKota="Bandung",
            email=fake.email(),
            noHandphone=fake.phone_number(),
        ),
        Alamat(
            tipeAlamat="tetap",
            alamat=fake.street_address(),
            kodePos=fake.postcode(),
            kodeKota="JKT",
            negara="Indonesia",
            noKontak=fake.phone_number(),
            namaKota="Jakarta",
            email=fake.email(),
            noHandphone=fake.phone_number(),
        )
    ]

    if add_third:
        base.append(
            Alamat(
                tipeAlamat=random.choice(["penanggung jawab", "darurat"]),
                alamat=fake.street_address(),
                kodePos=fake.postcode(),
                kodeKota=random.choice(["BDG","JKT","SBY"]),
                negara="Indonesia",
                noKontak=fake.phone_number(),
                namaKota=fake.city(),
                email=fake.email(),
                noHandphone=fake.phone_number(),
            )
        )

    return base

def random_orang_tua():
    return [
        OrangTua(
            nama=fake.name_male(),
            hubungan="Ayah",
            penghasilanKotor=float(fake.random_int(min=5_000_000, max=30_000_000)),
            pekerjaan="Karyawan Swasta",
            instansiBekerja=fake.company(),
            pendidikan=random.choice(["SMA","S1","S2"]),
        ),
        OrangTua(
            nama=fake.name_female(),
            hubungan="Ibu",
            penghasilanKotor=float(fake.random_int(min=3_000_000, max=20_000_000)),
            pekerjaan="Ibu Rumah Tangga",
            instansiBekerja=None,
            pendidikan=random.choice(["SMA","S1"]),
        )
    ]

def random_status_keuangan():
    sk_list = []

    # pilih jumlah semester 3–5 dengan rata2 ≈ 4
    num_sem = random.choice([3, 4, 4, 5])  # 3,4,4,5 → avg 4
    for sem in range(1, num_sem + 1):
        tagihan = float(fake.random_int(min=5_000_000, max=15_000_000))
        pembayaran = tagihan if random.random() > 0.2 else tagihan * 0.5
        sk_list.append(StatusKeuangan(
            semester=sem,
            tagihan=tagihan,
            pembayaran=pembayaran,
        ))
    return sk_list


def random_tugas_akhir(dosen_list):
    pembimbing1 = random.choice(dosen_list)["nip"]
    pembimbing2 = random.choice(dosen_list)["nip"]
    return TugasAkhir(
        judulBahasaInggris="Analysis of Academic Information Systems Using NoSQL",
        judulBahasaIndonesia="Analisis Sistem Informasi Akademik Menggunakan NoSQL",
        dosenPembimbing1=pembimbing1,
        dosenPembimbing2=pembimbing2,
    )

def random_alumni(nim):
    return Alumni(
        nomorIjazah=f"IJZ-{nim}",
        tanggalLulus=datetime(2024, 7, 31),
        gelar="S.T.",
        predikat=random.choice(["Memuaskan","Sangat Memuaskan","Cum Laude"]),
    )

def seed_mahasiswa(n=NUM_MAHASISWA):
    db.mahasiswa.delete_many({})

    dosen_docs = list(db.dosen.find({}))
    prodi_list = list(db.program_studi.find({}))

    if not prodi_list:
        raise RuntimeError("Program_studi must be seeded before mahasiswa")

    mahasiswa_docs = []
    used_nim = set()

    for _ in range(n):
        prodi = random.choice(prodi_list)
        kode_prodi = prodi["kodeProdi"]
        kode_fak = prodi["kodeFakultas"]

        # NIM unik 10 digit
        while True:
            nim = f"{fake.random_number(digits=10):010d}"
            if nim not in used_nim:
                used_nim.add(nim)
                break

        tahun_masuk = random.choice([2018, 2019, 2020, 2021, 2022])
        dosen_wali = random.choice(dosen_docs)["nip"] if dosen_docs else None

        # probabilitas agar jumlah TA & alumni ~2.6k / 33k ≈ 0.08
        has_ta = random.random() < 0.08
        has_alumni = random.random() < 0.08

        m = Mahasiswa(
            nim=nim,
            namaLengkap=fake.name(),
            kelas=random.choice(["A","B","C","D"]),
            tahunMasuk=tahun_masuk,
            kodeFakultas=kode_fak,
            kodeProdi=kode_prodi,
            noRegistrasi=str(fake.random_number(digits=8)),
            username=None,
            dosenWali=dosen_wali,
            biodata=random_biodata(),
            alamat=random_alamat(),
            orangTua=random_orang_tua(),
            statusKeuangan=random_status_keuangan(),
            tugasAkhir=random_tugas_akhir(dosen_docs) if has_ta else None,
            alumni=random_alumni(nim) if has_alumni else None,
        )

        mahasiswa_docs.append(m.model_dump())

    if mahasiswa_docs:
        db.mahasiswa.insert_many(mahasiswa_docs)
    print("Inserted mahasiswa:", len(mahasiswa_docs))
    return mahasiswa_docs

def seed_mata_kuliah(n_per_prodi=22):
    db.mata_kuliah.delete_many({})

    kategori_choices = ['WP','WI','WO','PB']
    prodi_list = list(db.program_studi.find({}))

    docs = []
    for prodi in prodi_list:
        kode_prodi = prodi["kodeProdi"]
        prefix = kode_prodi  # biar kode jelas PR001xxx, dll.

        for i in range(1, n_per_prodi + 1):
            kode = f"{prefix}{100 + i}"
            docs.append({
                "kodeMatkul": kode,
                "namaMk": f"Matakuliah {prefix}-{i}",
                "kategori": random.choice(kategori_choices),
                "sks": random.choice([2, 3, 4]),
                "cpmk": fake.sentence(nb_words=8),
                "kodeProdi": kode_prodi,
            })

    db.mata_kuliah.insert_many(docs)
    print("Inserted mata_kuliah:", len(docs))
    return docs

def seed_kurikulum():
    db.kurikulum.delete_many({})

    mata_kuliah = list(db.mata_kuliah.find({}))
    prodi_list = list(db.program_studi.find({}))

    docs = []
    for prodi in prodi_list:
        kode_prodi = prodi["kodeProdi"]
        mk_prodi = [mk for mk in mata_kuliah if mk["kodeProdi"] == kode_prodi]

        tahun = 2024
        mk_kurikulum = []
        total_sks = 0

        for mk in mk_prodi:
            mk_kurikulum.append({
                "kodeMatkul": mk["kodeMatkul"],
                "sks": mk["sks"],
            })
            total_sks += mk["sks"]

        docs.append({
            "kodeProdi": kode_prodi,
            "tahun": tahun,
            "namaKurikulum": f"Kurikulum {kode_prodi} {tahun}",
            "status": True,
            "sksLulusMinimal": min(total_sks, 144),
            "mataKuliah": mk_kurikulum,
        })

    if docs:
        db.kurikulum.insert_many(docs)
    print("Inserted kurikulum:", len(docs))
    return docs

def seed_ruangan(n=150):
    db.ruangan.delete_many({})
    docs = []
    for i in range(1, n + 1):
        kode = f"R{i:03d}"
        docs.append({
            "kodeRuangan": kode,
            "namaRuangan": f"Ruang Kuliah {i}",
            "deskripsi": fake.sentence(),
        })
    db.ruangan.insert_many(docs)
    print("Inserted ruangan:", len(docs))
    return docs


def seed_akun():
    db.akun.delete_many({})
    docs = []

    # akun dosen
    dosen_list = list(db.dosen.find({}))
    for d in dosen_list:
        username = f"dosen_{d['nip'][-5:]}"
        docs.append({
            "username": username,
            "password": "hashed_password_dummy",
            "tipe": "dosen",
        })

    # akun mahasiswa (akan di-link belakangan)
    mhs_list = list(db.mahasiswa.find({}))
    for m in mhs_list:
        username = f"mhs_{m['nim']}"
        docs.append({
            "username": username,
            "password": "hashed_password_dummy",
            "tipe": "mahasiswa",
        })

    if docs:
        db.akun.insert_many(docs)
    print("Inserted akun:", len(docs))
    return docs

def seed_akun_dosen():
    db.akun_dosen.delete_many({})

    dosen_list = list(db.dosen.find({}))
    akun_list = list(db.akun.find({"tipe": "dosen"}))
    akun_by_suffix = {a["username"].split("_")[-1]: a["username"] for a in akun_list}

    docs = []
    for d in dosen_list:
        suffix = d["nip"][-5:]
        username = akun_by_suffix.get(suffix)
        if username:
            docs.append({
                "username": username,
                "nip": d["nip"],
            })
    if docs:
        db.akun_dosen.insert_many(docs)
    print("Inserted akun_dosen:", len(docs))
    return docs

def seed_calon_mahasiswa_baru():
    db.calon_mahasiswa_baru.delete_many({})

    docs = []
    for i in range(100):
        no_reg = f"REG{fake.random_number(digits=6):06d}"
        docs.append({
            "noRegistrasi": no_reg,
            "preferensiBank": random.choice(["Mandiri","BNI","BRI","BTN","BCA"]),
            "sertifikatBahasaInggris": random.choice(["TOEFL ITP","TOEFL iBT","IELTS","TOEIC"]),
            "tesPotensiAkademik": random.choice(["TPA OTO Bappenas","Lainnya"]),
        })

    if docs:
        db.calon_mahasiswa_baru.insert_many(docs)

    # assign noRegistrasi ke sebagian mahasiswa
    mhs_list = list(db.mahasiswa.find({}))
    regs = [d["noRegistrasi"] for d in docs]
    for m in mhs_list:
        if random.random() > 0.5 and regs:
            db.mahasiswa.update_one(
                {"_id": m["_id"]},
                {"$set": {"noRegistrasi": random.choice(regs)}}
            )

    print("Inserted calon_mahasiswa_baru:", len(docs))
    return docs

def seed_rencana_studi():
    db.rencana_studi.delete_many({})

    mhs_list = list(db.mahasiswa.find({}))
    kurikulum_list = list(db.kurikulum.find({}))
    nilai_enum = ['A','AB','B','BC','C','D','E','F','T','P']

    kur_by_prodi = {k["kodeProdi"]: k for k in kurikulum_list}

    docs = []

    for m in mhs_list:
        # 4 rencana studi per mahasiswa (misal 4 semester)
        for sem in [1, 2, 3, 4]:
            tahun_ajaran = "2024/2025"
            kur = kur_by_prodi.get(m["kodeProdi"])
            if not kur:
                continue

            all_mk = kur["mataKuliah"]
            if len(all_mk) == 0:
                continue

            # ambil 7 matkul random per rencana studi
            mk_list = random.sample(all_mk, min(TARGET_MK_PER_RS, len(all_mk)))

            mata_kuliah_rs = []
            for mk in mk_list:
                mata_kuliah_rs.append({
                    "kodeProdi": m["kodeProdi"],
                    "tahun": kur["tahun"],
                    "kodeMatkul": mk["kodeMatkul"],
                    "disetujui": random.random() > 0.1,
                    "nilai": random.choice(nilai_enum) if sem < 4 else None,
                })

            docs.append({
                "nim": m["nim"],
                "tahunAjaran": tahun_ajaran,
                "semester": sem,
                "pembayaranUkt": True,
                "maksimalBeban": 24,
                "mataKuliah": mata_kuliah_rs,
            })

    if docs:
        db.rencana_studi.insert_many(docs)
    print("Inserted rencana_studi:", len(docs))
    return docs

def seed_dosen_pengampu():
    db.dosen_pengampu.delete_many({})

    dosen_list = list(db.dosen.find({}))
    kurikulum_list = list(db.kurikulum.find({}))
    prodi_list = list(db.program_studi.find({}))
    prodi_by_kode = {p["kodeProdi"]: p for p in prodi_list}

    docs = []
    # ambil 20 matkul per kurikulum → 140 * 20 ≈ 2,800 (dekat dengan 2,650)
    for kur in kurikulum_list:
        kode_prodi = kur["kodeProdi"]
        tahun = kur["tahun"]
        mk_list = kur["mataKuliah"][:20]

        prodi = prodi_by_kode.get(kode_prodi)
        if not prodi:
            continue

        fk = prodi["kodeFakultas"]
        dosen_prodi = [d for d in dosen_list if d["kodeFakultas"] == fk]

        for mk in mk_list:
            if not dosen_prodi:
                continue
            d = random.choice(dosen_prodi)
            docs.append({
                "kodeProdi": kode_prodi,
                "tahun": tahun,
                "kodeMatkul": mk["kodeMatkul"],
                "nipDosen": d["nip"],
                "kelas": random.choice(["A","B"]),
            })

    if docs:
        db.dosen_pengampu.insert_many(docs)
    print("Inserted dosen_pengampu:", len(docs))
    return docs

def seed_jadwal_kuliah():
    db.jadwal_kuliah.delete_many({})

    pengampu_list = list(db.dosen_pengampu.find({}))
    ruangan_list = list(db.ruangan.find({}))
    mhs_list = list(db.mahasiswa.find({}))

    docs = []
    for p in pengampu_list:
        if not ruangan_list:
            continue
        r = random.choice(ruangan_list)

        base_date = datetime(2024, 9, 1)
        # 12 pertemuan per matkul → 2,800 * 12 ≈ 33,600 (dekat 35,525)
        for week in range(1, 13):
            tanggal = base_date + timedelta(weeks=week-1)
            jam_mulai = "08:00"
            jam_selesai = "09:40"

            # 30–40 peserta per pertemuan → avg ≈ 33 → 33,600*33 ≈ 1,1M
            num_peserta = random.randint(30, 40)
            peserta = random.sample(mhs_list, min(len(mhs_list), num_peserta))

            kehadiran = []
            for m in peserta:
                kehadiran.append({
                    "nim": m["nim"],
                    "isHadir": random.random() > 0.2,
                })

            docs.append({
                "kodeProdi": p["kodeProdi"],
                "tahun": p["tahun"],
                "kodeMatkul": p["kodeMatkul"],
                "nipDosen": p["nipDosen"],
                "kodeRuangan": r["kodeRuangan"],
                "tanggal": tanggal,
                "jamMulai": jam_mulai,
                "jamSelesai": jam_selesai,
                "kehadiran": kehadiran,
            })

    if docs:
        db.jadwal_kuliah.insert_many(docs)
    print("Inserted jadwal_kuliah:", len(docs))
    return docs

def seed_wisuda_dan_ijazah():
    mhs_list = list(db.mahasiswa.find({}))
    for m in mhs_list:
        # ~7–8% dari mahasiswa jadi calon wisuda + pengambilan ijazah
        if random.random() < 0.08:
            calon = {
                "jalur": random.choice(["Reguler","Fast Track"]),
                "nama": m["namaLengkap"],
                "tanggalSidang": datetime(2024, 7, random.randint(1, 28)),
                "statusPengisianKuesioner": random.random() > 0.3,
                "statusPendaftaranWisuda": random.random() > 0.2,
            }

            pengambilan = [{
                "periodeWisuda": "2024/3",
                "jadwalPengambilan": datetime(2024, 8, random.randint(1, 28)),
                "loket": random.choice(["Loket 1","Loket 2"]),
                "waktuPengambilan": "09:00",
            }]

            db.mahasiswa.update_one(
                {"_id": m["_id"]},
                {
                    "$set": {
                        "calonPesertaWisuda": calon,
                        "pengambilanIjazah": pengambilan,
                    }
                }
            )
    print("Updated mahasiswa with wisuda & pengambilan ijazah")
