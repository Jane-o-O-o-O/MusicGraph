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

MERGE (jolin:Person {id: 'person_jolin_tsai'})
SET jolin.name = '蔡依林',
    jolin.type = 'Person',
    jolin.aliases = ['Jolin Tsai'],
    jolin.summary = 'Taiwanese pop singer with several notable cross-artist collaborations.',
    jolin.roles = ['Singer'],
    jolin.country = 'CN',
    jolin.popularity = 91;

MERGE (ashin:Person {id: 'person_ashin'})
SET ashin.name = '阿信',
    ashin.type = 'Person',
    ashin.aliases = ['Ashin'],
    ashin.summary = 'Lead vocalist and songwriter of Mayday.',
    ashin.roles = ['Singer', 'Songwriter'],
    ashin.country = 'CN',
    ashin.popularity = 90;

MERGE (monster:Person {id: 'person_monster'})
SET monster.name = '怪兽',
    monster.type = 'Person',
    monster.aliases = ['Monster'],
    monster.summary = 'Guitarist and songwriter in Mayday.',
    monster.roles = ['Guitarist', 'Composer'],
    monster.country = 'CN',
    monster.popularity = 82;

MERGE (masa:Person {id: 'person_masa'})
SET masa.name = '玛莎',
    masa.type = 'Person',
    masa.aliases = ['Masa'],
    masa.summary = 'Bassist in Mayday.',
    masa.roles = ['Bassist'],
    masa.country = 'CN',
    masa.popularity = 79;

MERGE (stone:Person {id: 'person_stone'})
SET stone.name = '石头',
    stone.type = 'Person',
    stone.aliases = ['Stone'],
    stone.summary = 'Guitarist in Mayday.',
    stone.roles = ['Guitarist'],
    stone.country = 'CN',
    stone.popularity = 78;

MERGE (ming:Person {id: 'person_ming'})
SET ming.name = '冠佑',
    ming.type = 'Person',
    ming.aliases = ['Ming'],
    ming.summary = 'Drummer in Mayday.',
    ming.roles = ['Drummer'],
    ming.country = 'CN',
    ming.popularity = 77;

MERGE (mayday:Band {id: 'band_mayday'})
SET mayday.name = '五月天',
    mayday.type = 'Band',
    mayday.aliases = ['Mayday'],
    mayday.summary = 'One of the best-known Mandarin rock bands.',
    mayday.country = 'CN',
    mayday.formed_year = 1997,
    mayday.popularity = 94;

MERGE (qinghuaci:Work {id: 'work_qinghuaci'})
SET qinghuaci.name = '青花瓷',
    qinghuaci.type = 'Work',
    qinghuaci.aliases = ['Blue and White Porcelain'],
    qinghuaci.summary = 'One of Jay Chou''s best-known songs.',
    qinghuaci.language = 'zh',
    qinghuaci.release_date = date('2007-11-02'),
    qinghuaci.duration_seconds = 239,
    qinghuaci.popularity = 96;

MERGE (daoxiang:Work {id: 'work_daoxiang'})
SET daoxiang.name = '稻香',
    daoxiang.type = 'Work',
    daoxiang.aliases = ['Rice Aroma'],
    daoxiang.summary = 'A warm and uplifting Jay Chou song.',
    daoxiang.language = 'zh',
    daoxiang.release_date = date('2008-10-15'),
    daoxiang.duration_seconds = 223,
    daoxiang.popularity = 95;

MERGE (caihong:Work {id: 'work_caihong'})
SET caihong.name = '彩虹',
    caihong.type = 'Work',
    caihong.aliases = ['Rainbow'],
    caihong.summary = 'A mellow Jay Chou ballad.',
    caihong.language = 'zh',
    caihong.release_date = date('2007-11-02'),
    caihong.duration_seconds = 263,
    caihong.popularity = 87;

MERGE (prague:Work {id: 'work_bulagguangchang'})
SET prague.name = '布拉格广场',
    prague.type = 'Work',
    prague.aliases = ['Prague Square'],
    prague.summary = 'A crossover work associated with Jolin Tsai, Jay Chou, and Vincent Fang.',
    prague.language = 'zh',
    prague.release_date = date('2003-03-07'),
    prague.duration_seconds = 292,
    prague.popularity = 86;

MERGE (juejiang:Work {id: 'work_juejiang'})
SET juejiang.name = '倔强',
    juejiang.type = 'Work',
    juejiang.aliases = ['Stubborn'],
    juejiang.summary = 'Mayday anthem from Shen De Hai Zi Dou Zai Tiao Wu.',
    juejiang.language = 'zh',
    juejiang.release_date = date('2004-11-05'),
    juejiang.duration_seconds = 262,
    juejiang.popularity = 89;

MERGE (wenrou:Work {id: 'work_wenrou'})
SET wenrou.name = '温柔',
    wenrou.type = 'Work',
    wenrou.aliases = ['Tenderness'],
    wenrou.summary = 'One of Mayday''s most recognizable early ballads.',
    wenrou.language = 'zh',
    wenrou.release_date = date('2000-07-07'),
    wenrou.duration_seconds = 269,
    wenrou.popularity = 88;

MERGE (missingyou:Work {id: 'work_turanhaoxiangni'})
SET missingyou.name = '突然好想你',
    missingyou.type = 'Work',
    missingyou.aliases = ['Suddenly Missing You'],
    missingyou.summary = 'A signature Mayday stadium ballad.',
    missingyou.language = 'zh',
    missingyou.release_date = date('2008-10-23'),
    missingyou.duration_seconds = 265,
    missingyou.popularity = 92;

MERGE (womihenmang:Album {id: 'album_womihenmang'})
SET womihenmang.name = '我很忙',
    womihenmang.type = 'Album',
    womihenmang.aliases = [],
    womihenmang.summary = 'Jay Chou studio album released in 2007.',
    womihenmang.album_type = 'Studio',
    womihenmang.release_date = date('2007-11-02'),
    womihenmang.popularity = 85;

MERGE (mojiezuo:Album {id: 'album_mojiezuo'})
SET mojiezuo.name = '魔杰座',
    mojiezuo.type = 'Album',
    mojiezuo.aliases = ['Capricorn'],
    mojiezuo.summary = 'Jay Chou album released in 2008.',
    mojiezuo.album_type = 'Studio',
    mojiezuo.release_date = date('2008-10-15'),
    mojiezuo.popularity = 84;

MERGE (castle:Album {id: 'album_castle'})
SET castle.name = '城堡',
    castle.type = 'Album',
    castle.aliases = ['Castle'],
    castle.summary = 'Jolin Tsai album released in 2004.',
    castle.album_type = 'Studio',
    castle.release_date = date('2004-02-27'),
    castle.popularity = 82;

MERGE (shende:Album {id: 'album_shendehaizidouzaitiaowu'})
SET shende.name = '神的孩子都在跳舞',
    shende.type = 'Album',
    shende.aliases = ['People Life, Ocean Wild'],
    shende.summary = 'A milestone Mayday album from 2004.',
    shende.album_type = 'Studio',
    shende.release_date = date('2004-11-05'),
    shende.popularity = 86;

MERGE (secondlife:Album {id: 'album_second_life'})
SET secondlife.name = '第二人生',
    secondlife.type = 'Album',
    secondlife.aliases = ['Second Life'],
    secondlife.summary = 'Mayday album released in 2011.',
    secondlife.album_type = 'Studio',
    secondlife.release_date = date('2011-12-16'),
    secondlife.popularity = 87;

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

MERGE (ballad:Genre {id: 'genre_ballad'})
SET ballad.name = 'Ballad',
    ballad.type = 'Genre',
    ballad.aliases = [],
    ballad.summary = 'Emotion-driven melodic pop ballads.',
    ballad.description = 'Ballad music genre.';

MERGE (jay)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(qinghuaci);
MERGE (jay)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(qinghuaci);
MERGE (fang)-[:WROTE_LYRICS_FOR {source: 'seed', confidence: 1.0}]->(qinghuaci);
MERGE (qinghuaci)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(womihenmang);
MERGE (qinghuaci)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(pop);
MERGE (qinghuaci)-[:HAS_GENRE {source: 'seed', confidence: 0.8}]->(ballad);
MERGE (jay)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(daoxiang);
MERGE (jay)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(daoxiang);
MERGE (fang)-[:WROTE_LYRICS_FOR {source: 'seed', confidence: 1.0}]->(daoxiang);
MERGE (daoxiang)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(mojiezuo);
MERGE (daoxiang)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(pop);
MERGE (jay)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(caihong);
MERGE (jay)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(caihong);
MERGE (fang)-[:WROTE_LYRICS_FOR {source: 'seed', confidence: 1.0}]->(caihong);
MERGE (caihong)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(womihenmang);
MERGE (caihong)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(ballad);
MERGE (jolin)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(prague);
MERGE (jay)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(prague);
MERGE (fang)-[:WROTE_LYRICS_FOR {source: 'seed', confidence: 1.0}]->(prague);
MERGE (prague)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(castle);
MERGE (prague)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(pop);
MERGE (ashin)-[:MEMBER_OF {source: 'seed', confidence: 1.0}]->(mayday);
MERGE (monster)-[:MEMBER_OF {source: 'seed', confidence: 1.0}]->(mayday);
MERGE (masa)-[:MEMBER_OF {source: 'seed', confidence: 1.0}]->(mayday);
MERGE (stone)-[:MEMBER_OF {source: 'seed', confidence: 1.0}]->(mayday);
MERGE (ming)-[:MEMBER_OF {source: 'seed', confidence: 1.0}]->(mayday);
MERGE (mayday)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(rock);
MERGE (mayday)-[:HAS_GENRE {source: 'seed', confidence: 0.7}]->(ballad);
MERGE (ashin)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(juejiang);
MERGE (ashin)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(juejiang);
MERGE (monster)-[:COMPOSED {source: 'seed', confidence: 0.9}]->(juejiang);
MERGE (juejiang)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(shende);
MERGE (juejiang)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(rock);
MERGE (ashin)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(wenrou);
MERGE (ashin)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(wenrou);
MERGE (wenrou)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(shende);
MERGE (wenrou)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(ballad);
MERGE (wenrou)-[:HAS_GENRE {source: 'seed', confidence: 0.7}]->(rock);
MERGE (ashin)-[:PERFORMED {source: 'seed', confidence: 1.0}]->(missingyou);
MERGE (ashin)-[:COMPOSED {source: 'seed', confidence: 1.0}]->(missingyou);
MERGE (monster)-[:COMPOSED {source: 'seed', confidence: 0.8}]->(missingyou);
MERGE (missingyou)-[:IN_ALBUM {source: 'seed', confidence: 1.0}]->(secondlife);
MERGE (missingyou)-[:HAS_GENRE {source: 'seed', confidence: 1.0}]->(ballad);
