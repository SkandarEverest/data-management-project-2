from seed_data import (
    seed_fakultas,
    seed_prodi,
    seed_dosen,
    seed_mahasiswa,
    seed_mata_kuliah,
    seed_kurikulum,
    seed_ruangan,
    seed_akun,
    seed_calon_mahasiswa_baru,
    seed_rencana_studi,
    seed_dosen_pengampu,
    seed_jadwal_kuliah,
    seed_wisuda_dan_ijazah,
)

def main():
    seed_fakultas()
    seed_prodi()
    seed_dosen()
    seed_mahasiswa()

    seed_mata_kuliah()
    seed_kurikulum()
    seed_ruangan()

    seed_akun()
    seed_calon_mahasiswa_baru()

    seed_rencana_studi()
    seed_dosen_pengampu()
    seed_jadwal_kuliah()

    seed_wisuda_dan_ijazah()

if __name__ == "__main__":
    main()
