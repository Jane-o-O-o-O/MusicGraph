MERGE (jay:Person {id: 'person_jay_chou'})
SET jay.name = '周杰伦',
    jay.type = 'Person',
    jay.aliases = ['Jay Chou'],
    jay.summary = 'Singer, composer, and producer.',
    jay.roles = ['Singer', 'Composer', 'Producer'],
    jay.country = 'CN',
    jay.popularity = 99;

MERGE (fang:Person {id: 'person_fang_wenshan'})
SET fang.name = '方文山',
    fang.type = 'Person',
    fang.aliases = ['Vincent Fang'],
    fang.summary = 'Lyricist known for long-running collaborations with Jay Chou.',
    fang.roles = ['Lyricist'],
    fang.country = 'CN',
    fang.popularity = 88;

MERGE (ashin:Person {id: 'person_ashin'})
SET ashin.name = '阿信',
    ashin.type = 'Person',
    ashin.aliases = ['Ashin'],
    ashin.summary = 'Lead vocalist and songwriter of Mayday.',
    ashin.roles = ['Singer', 'Songwriter'],
    ashin.country = 'CN',
    ashin.popularity = 90;

MERGE (song:Work {id: 'work_qinghuaci'})
SET song.name = '青花瓷',
    song.type = 'Work',
    song.aliases = ['Blue and White Porcelain'],
    song.summary = 'One of Jay Chou''s best-known songs.',
    song.language = 'zh',
    song.release_date = date('2007-11-02'),
    song.duration_seconds = 239,
    song.popularity = 96;

MERGE (album:Album {id: 'album_womihenmang'})
SET album.name = '我很忙',
    album.type = 'Album',
    album.aliases = [],
    album.summary = 'Jay Chou studio album released in 2007.',
    album.album_type = 'Studio',
    album.release_date = date('2007-11-02'),
    album.popularity = 85;

MERGE (mayday:Band {id: 'band_mayday'})
SET mayday.name = '五月天',
    mayday.type = 'Band',
    mayday.aliases = ['Mayday'],
    mayday.summary = 'One of the best-known Mandarin rock bands.',
    mayday.country = 'CN',
    mayday.formed_year = 1997,
    mayday.popularity = 94;

MERGE (juejiang:Work {id: 'work_juejiang'})
SET juejiang.name = '倔强',
    juejiang.type = 'Work',
    juejiang.aliases = ['Stubborn'],
    juejiang.summary = 'Mayday anthem from the album Shen de Hai Zi Dou Zai Tiao Wu.',
    juejiang.language = 'zh',
    juejiang.release_date = date('2004-11-05'),
    juejiang.duration_seconds = 262,
    juejiang.popularity = 89;

MERGE (pop:Genre {id: 'genre_pop'})
SET pop.name = 'Pop',
    pop.type = 'Genre',
    pop.aliases = ['Mandopop'],
    pop.summary = 'Popular music with mainstream audience reach.',
    pop.description = 'General popular music genre.';

MERGE (rock:Genre {id: 'genre_rock'})
SET rock.name = 'Rock',
    rock.type = 'Genre',
    rock.aliases = [],
    rock.summary = 'Rock-oriented sound and instrumentation.',
    rock.description = 'Rock music genre.';

MERGE (jay)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(song);
MERGE (jay)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(song);
MERGE (fang)-[:WROTE_LYRICS_FOR {source: 'seed', confidence: 1.0}]->(song);
MERGE (song)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(album);
MERGE (song)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(pop);
MERGE (ashin)-[:MEMBER_OF {source: 'seed', confidence: 1.0}]->(mayday);
MERGE (ashin)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(juejiang);
MERGE (ashin)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(juejiang);
MERGE (mayday)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(rock);
MERGE (juejiang)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(rock);
