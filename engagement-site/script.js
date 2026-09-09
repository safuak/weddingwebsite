const INVITE_URL = 'https://shandfi.com';
const EVENT_DATE = new Date('2026-09-26T19:00:00+03:00');
const REAL_UPLOAD_ENABLED = true;
const UPLOAD_ENDPOINT = '/api/memories/upload';

if (location.search && /(?:guestName|memories|name|guests|status|note)=/.test(location.search)) {
  history.replaceState(null, '', location.pathname + location.hash);
}

const translations = {
  bg: {
    gateSmall:'Покана за годеж', gateText:'Ще се радваме да бъдете с нас в този специален ден.', openInvite:'Продължи',
    navHome:'Начало', navStory:'История', navGallery:'Галерия', navSong:'Песен', navLocation:'Място', navRsvp:'Потвърдете', navUpload:'Спомени',
    navHomeShort:'Начало', navStoryShort:'История', navGalleryShort:'Галерия', navUploadShort:'Спомени', navRsvpShort:'RSVP',
    heroEyebrow:'Добре дошли', heroSub:'Годеж', heroInviteLine:'Имаме удоволствието да Ви поканим на нашия годеж', days:'дни', hours:'часа', minutes:'мин', seconds:'сек', reminderBtn:'Напомни ми', rsvpBtn:'Потвърди присъствие', inviteBtn:'Виж поканата',
    storyKicker:'Нашата малка история', storyTitle:'Нашата история', storySub:'Всяка любов започва с история',
    s1t:'Запознахме се', s1p:'Запознахме се в Non Stop.', s2t:'Говорихме с превод', s2p:'Не говорехме един език, но сърцата ни се разбраха.', s3t:'Първа среща', s3p:'Незабравим ден по улиците на София.', s4t:'Първа целувка', s4p:'В този момент всичко се промени.', s5t:'Годеж', s5p:'И сега казваме „да“ завинаги.',
    translateTitle:'История, започнала с превод', translateFinal:'Различни езици, едно сърце.',
    galleryKicker:'Белезите на бялата гюл', galleryTitle:'Нашата галерия', gallerySub:'Всички спомени в малки картички, готови да се разтворят.', all:'Всички', sofiaDays:'Софийски дни', family:'Семейство', engagement:'Годеж', us:'Ние',
    songKicker:'Мелодията ни', songTitle:'Нашата песен', songSub:'Тази песен разказва за нас', spotify:'Слушай в Spotify',
    uploadKicker:'Дигитална кутия за спомени', uploadTitle:'Да запазим спомените', uploadSub:'Споделете снимките и видеата, които сте направили', uploadH3:'Качете вашите снимки и видеа', uploadText:'Изпратете вашите снимки и видеа. Нека спомените ни растат заедно с вас. Всеки кадър е много ценен за нас.', uploadThanksTitle:'Благодарим Ви!', uploadThanksText:'Спомените ви стигнаха до нас. Благодарим, че направихте деня ни още по-специален.', fullName:'Име и фамилия', namePh:'Напишете името си', emailOptional:'Имейл', emailPh:'по желание', shortNote:'Кратка бележка', memoryNotePh:'Оставете кратка бележка...', chooseFiles:'Изберете файлове', fileTypes:'Можете да изберете снимки и видеа; те ще се качват едно по едно.', noFile:'Няма избран файл', uploadBtn:'Качи спомените', vdsNote:'', storyCopy:'От първата среща до момента, в който казахме „да“ – всяка стъпка е част от нашата приказка.', dateLabel:'Дата', timeLabel:'Час', placeLabel:'Място',

    startTime:'Започва в 19:00',
    locationKicker:'Къде и кога', locationTitle:'Място на годежа', locationSub:'Ще се радваме да бъдете с нас', directions:'Упътване', programTitle:'Програма', welcome:'Посрещане', ceremony:'Годежна церемония', dinner:'Вечеря', fun:'Забавление',
    rsvpKicker:'Моля, потвърдете', rsvpTitle:'Потвърждение', rsvpSub:'Моля, потвърдете дали ще присъствате', guestCount:'Колко души ще присъстват?', select:'Изберете', coming:'Ще присъствам', notComing:'Няма да присъствам', note:'Бележка', notePh:'Оставете ни кратко послание...', send:'Изпрати',
    quote:'“Различни езици, различни пътища... Но едно сърце.”', finalTop:'С нетърпение очакваме да споделим този', finalScript:'специален ден с Вас', finalThanks:'Благодарим Ви, че ще бъдете част от нашия годеж и ще споделите нашето щастие.', finalAwait:'Очакваме Ви', rsvpAlert:'Вашето потвърждение е получено. Благодарим ви ❤️', uploadAlert:'Файловете са качени успешно.', uploadDone:'Успешно изпратено', uploadFailed:'Качването не бе успешно.', uploadConnection:'Грешка при връзката за качване.', uploadResponse:'Грешка в отговора при качване.', invalidFile:'Невалиден тип файл.', fileTooLarge:'Файлът е твърде голям.', rsvpError:'Грешка при изпращане.', fileSelected:'избрани', retryUpload:'Качи отново', linkCopied:'Линкът е копиран', calendarDownloaded:'Календарният файл е изтеглен', audioOn:'Спри звука', audioOff:'Пусни звука', audioToggleLabel:'Музика', qrKicker:'Маса за спомени', qrText:'Изберете как искате да продължите.', qrInvite:'Към поканата', qrMemories:'Сподели спомени'
  },
  tr: {
    gateSmall:'Nişan Davetiyesi', gateText:'Bu özel günümüzde sizi de aramızda görmekten mutluluk duyarız.', openInvite:'Devam Et',
    navHome:'Ana Sayfa', navStory:'Hikayemiz', navGallery:'Galeri', navSong:'Şarkımız', navLocation:'Nişan Yeri', navRsvp:'Katılım', navUpload:'Anılar',
    navHomeShort:'Ana', navStoryShort:'Hikaye', navGalleryShort:'Galeri', navUploadShort:'Anılar', navRsvpShort:'RSVP',
    heroEyebrow:'Hoş geldiniz', heroSub:'Nişanlanıyoruz', heroInviteLine:'Bu mutlu günümüzü sizinle paylaşmak istiyoruz', days:'gün', hours:'saat', minutes:'dk', seconds:'sn', reminderBtn:'Hatırlatıcı Al', rsvpBtn:'Katılım Bildir', inviteBtn:'Davetiyeyi Gör',
    storyKicker:'Küçük hikayemiz', storyTitle:'Hikayemiz', storySub:'Her aşk bir hikayeyle başlar',
    s1t:'Tanıştık', s1p:"Non Stop'ta tanıştık.", s2t:'Çeviriyle Konuştuk', s2p:'Aynı dili konuşmasak da kalplerimiz anlaştı.', s3t:'İlk Buluşma', s3p:'Sofia sokaklarında unutulmaz bir gün.', s4t:'İlk Öpücük', s4p:'O an, her şey değişti.', s5t:'Nişan', s5p:'Ve şimdi sonsuza “evet” diyoruz.',
    translateTitle:'Çeviriyle başlayan hikaye', translateFinal:'Farklı diller, tek kalp.',
    galleryKicker:'Beyaz Gül Anıları', galleryTitle:'Galerimiz', gallerySub:'Tüm anılar küçük kartlarda, üzerine tıklayınca açılır.', all:'Tümü', sofiaDays:'Sofia Günleri', family:'Aile', engagement:'Nişan', us:'Biz',
    songKicker:'Melodimiz', songTitle:'Bizim Şarkımız', songSub:'Bu şarkı bizi anlatır', spotify:"Spotify'da Dinle",
    uploadKicker:'Dijital anı kutusu', uploadTitle:'Anılarımızı Saklayalım', uploadSub:'Çektiğiniz fotoğraf ve videoları bizimle paylaşın', uploadH3:'Fotoğraf ve Videolarınızı Yükleyin', uploadText:'Fotoğraf ve videolarınızı gönderin. Anılarımız sizinle birlikte çoğalsın. Her fotoğraf ve video bizim için çok değerli.', uploadThanksTitle:'Çok teşekkür ederiz!', uploadThanksText:'Anılarınız bize ulaştı. Bu güzel günü bizimle birlikte büyüttüğünüz için çok mutluyuz.', fullName:'Ad Soyad', namePh:'Adınızı yazın', emailOptional:'E-posta', emailPh:'isteğe bağlı', shortNote:'Kısa Not', memoryNotePh:'Kısa bir not bırakın...', chooseFiles:'Dosya seçin', fileTypes:'Fotoğraf ve video seçebilirsiniz; dosyalar sırayla yüklenecek.', noFile:'Henüz dosya seçilmedi', uploadBtn:'Anıları Yükle', vdsNote:'', storyCopy:'İlk buluşmadan “evet”e kadar her an bizim hikayemizin bir parçası.', dateLabel:'Tarih', timeLabel:'Saat', placeLabel:'Yer',

    startTime:'19:00' ,
    locationKicker:'Nerede ve ne zaman', locationTitle:'Nişan Yeri', locationSub:'Sizleri de aramızda görmekten mutluluk duyarız', directions:'Yol Tarifi Al', programTitle:'Tören Programı', welcome:'Karşılama', ceremony:'Nişan Töreni', dinner:'Yemek', fun:'Eğlence',
    rsvpKicker:'Lütfen bildiriniz', rsvpTitle:'Katılım Durumu', rsvpSub:'Lütfen katılım durumunuzu bildirin', guestCount:'Kaç kişi katılacaksınız?', select:'Seçiniz', coming:'Geliyorum', notComing:'Gelemiyorum', note:'Not', notePh:'Bizim için bir not bırakın...', send:'Gönder',
    quote:'“Farklı diller, farklı yollar... Ama aynı kalp.”', finalTop:'Bu özel günü sizinle paylaşmayı sabırsızlıkla bekliyoruz', finalScript:'en mutlu günümüzde', finalThanks:'Nişanımızın bir parçası olup mutluluğumuzu paylaşacağınız için teşekkür ederiz.', finalAwait:'Sizi bekliyoruz', rsvpAlert:'Katılım bilginiz alındı. Teşekkür ederiz ❤️', uploadAlert:'Dosyalar başarıyla yüklendi.', uploadDone:'Başarıyla gönderildi', uploadFailed:'Yükleme başarısız oldu.', uploadConnection:'Yükleme bağlantı hatası.', uploadResponse:'Yükleme yanıtı okunamadı.', invalidFile:'Geçersiz dosya türü.', fileTooLarge:'Dosya çok büyük.', rsvpError:'Gönderim hatası.', fileSelected:'dosya seçildi', retryUpload:'Yeniden yükle', linkCopied:'Link kopyalandı', calendarDownloaded:'Takvim dosyası indirildi', audioOn:'Sesi kapat', audioOff:'Sesi aç', audioToggleLabel:'Müzik', qrKicker:'Anı Masası', qrText:'Nasıl devam etmek istersiniz?', qrInvite:'Davetiyeye Git', qrMemories:'Anıları Paylaş'
  },
  en: {
    gateSmall:'Engagement Invitation', gateText:'We would be happy to have you with us on this special day.', openInvite:'Continue',
    navHome:'Home', navStory:'Story', navGallery:'Gallery', navSong:'Song', navLocation:'Location', navRsvp:'RSVP', navUpload:'Memories',
    navHomeShort:'Home', navStoryShort:'Story', navGalleryShort:'Gallery', navUploadShort:'Memories', navRsvpShort:'RSVP',
    heroEyebrow:'Welcome', heroSub:"We're getting engaged", heroInviteLine:'We would love to share this happy day with you', days:'days', hours:'hours', minutes:'min', seconds:'sec', reminderBtn:'Get Reminder', rsvpBtn:'RSVP', inviteBtn:'See Invitation',
    storyKicker:'Our little story', storyTitle:'Our Story', storySub:'Every love begins with a story',
    s1t:'We Met', s1p:'We met at Non Stop.', s2t:'We Talked with Translation', s2p:'We did not speak the same language, but our hearts understood.', s3t:'First Date', s3p:'An unforgettable day in the streets of Sofia.', s4t:'First Kiss', s4p:'In that moment, everything changed.', s5t:'Engagement', s5p:'And now, we say “yes” forever.',
    translateTitle:'A story that started with translation', translateFinal:'Different languages, one heart.',
    galleryKicker:'White Rose Memories', galleryTitle:'Our Gallery', gallerySub:'All memories in small cards, ready to open.', all:'All', sofiaDays:'Sofia Days', family:'Family', engagement:'Engagement', us:'Us',
    songKicker:'Our melody', songTitle:'Our Song', songSub:'This song tells our story', spotify:'Listen on Spotify',
    uploadKicker:'Digital memory box', uploadTitle:'Let’s Keep Our Memories', uploadSub:'Share the photos and videos you took with us', uploadH3:'Upload Your Photos and Videos', uploadText:'Send us your photos and videos. Let our memories grow together with you. Every photo and video is very precious to us.', uploadThanksTitle:'Thank you so much!', uploadThanksText:'Your memories reached us. Thank you for making this day even more special with us.', fullName:'Full Name', namePh:'Write your name', emailOptional:'Email', emailPh:'optional', shortNote:'Short Note', memoryNotePh:'Leave a short note...', chooseFiles:'Choose files', fileTypes:'Choose photos and videos; files will upload one by one.', noFile:'No file selected', uploadBtn:'Upload Memories', vdsNote:'', storyCopy:'From the first date to “yes”, every moment is part of our story.', dateLabel:'Date', timeLabel:'Time', placeLabel:'Place',

    startTime:'Starts at 19:00',
    locationKicker:'Where and when', locationTitle:'Engagement Location', locationSub:'We would be happy to see you with us', directions:'Get Directions', programTitle:'Ceremony Program', welcome:'Welcome', ceremony:'Engagement Ceremony', dinner:'Dinner', fun:'Celebration',
    rsvpKicker:'Please confirm', rsvpTitle:'RSVP', rsvpSub:'Please let us know if you will attend', guestCount:'How many guests?', select:'Select', coming:'I am coming', notComing:'I cannot come', note:'Note', notePh:'Leave us a short message...', send:'Send',
    quote:'“Different languages, different roads... But the same heart.”', finalTop:'We cannot wait to share this', finalScript:'special day with you', finalThanks:'Thank you for being part of our engagement and sharing our happiness.', finalAwait:'We are waiting for you', rsvpAlert:'Your RSVP has been received. Thank you ❤️', uploadAlert:'Files uploaded successfully.', uploadDone:'Uploaded successfully', uploadFailed:'Upload failed.', uploadConnection:'Upload connection error.', uploadResponse:'Upload response error.', invalidFile:'Invalid file type.', fileTooLarge:'File is too large.', rsvpError:'Submission error.', fileSelected:'files selected', retryUpload:'Upload again', linkCopied:'Link copied', calendarDownloaded:'Calendar file downloaded', audioOn:'Mute', audioOff:'Play sound', audioToggleLabel:'Music', qrKicker:'Memory Table', qrText:'Choose how you would like to continue.', qrInvite:'Go to Invitation', qrMemories:'Share Memories'
  }
};

let currentLang = localStorage.getItem('siteLang') || 'bg';
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const t = key => translations[currentLang]?.[key] || translations.bg[key] || key;
let selectedMemoryFiles = [];
document.documentElement.classList.add('gate-locked');
document.body.classList.add('gate-locked');

function toast(message){
  const el = $('#toast');
  if(!el) return alert(message);
  el.textContent = message;
  el.classList.add('show');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => el.classList.remove('show'), 2600);
}

function applyLanguage(lang){
  currentLang = translations[lang] ? lang : 'bg';
  localStorage.setItem('siteLang', currentLang);
  document.documentElement.lang = currentLang;
  $$('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (translations[currentLang][key]) el.textContent = translations[currentLang][key];
  });
  $$('[data-placeholder]').forEach(el => {
    const key = el.dataset.placeholder;
    if (translations[currentLang][key]) el.placeholder = translations[currentLang][key];
  });
  $$('[data-lang]').forEach(btn => btn.classList.toggle('active', btn.dataset.lang === currentLang));
  updateFileCount();
  updateAudioControl();
}

function openInvitation(){
  const gate = $('#inviteGate');
  if(gate?.classList.contains('opening')) return;
  burstDoorSparks();
  gate?.classList.add('opening');
  startSiteAudio();
  setTimeout(() => {
    gate?.classList.add('hide');
    document.documentElement.classList.remove('gate-locked');
    document.body.classList.remove('gate-locked');
  }, 1250);
  setTimeout(() => $('#home')?.scrollIntoView({behavior:'smooth'}), 900);
}

function burstDoorSparks(){
  const layer = $('#sparkLayer');
  if(!layer) return;
  layer.innerHTML = '';
  const sparkCount = window.matchMedia('(max-width: 520px)').matches ? 34 : 54;
  for(let index = 0; index < sparkCount; index += 1){
    const spark = document.createElement('span');
    const angle = (Math.PI * 2 * index / sparkCount) + (Math.random() * .55);
    const distance = 70 + Math.random() * (window.innerWidth > 760 ? 300 : 170);
    const drift = (Math.random() - .5) * 90;
    const x = Math.cos(angle) * distance * .42 + drift;
    const y = Math.sin(angle) * distance - Math.random() * 130;
    const size = 4 + Math.random() * 8;
    spark.className = `spark${index % 5 === 0 ? ' star' : ''}`;
    spark.style.setProperty('--spark-x', `${x.toFixed(1)}px`);
    spark.style.setProperty('--spark-y', `${y.toFixed(1)}px`);
    spark.style.setProperty('--spark-size', `${size.toFixed(1)}px`);
    spark.style.setProperty('--spark-duration', `${760 + Math.random() * 620}ms`);
    spark.style.setProperty('--spark-rotate', `${Math.round(Math.random() * 260 - 130)}deg`);
    spark.style.top = `${46 + Math.random() * 24}%`;
    layer.appendChild(spark);
  }
  setTimeout(() => { layer.innerHTML = ''; }, 1500);
}

function presentInvitation(){
  const gate = $('#inviteGate');
  gate?.classList.add('presented');
}

function resetInvitationGate(){
  const gate = $('#inviteGate');
  if(!gate) return;
  gate.classList.remove('hide', 'opening', 'presented');
  document.documentElement.classList.add('gate-locked');
  document.body.classList.add('gate-locked');
  window.scrollTo({top: 0, behavior: 'smooth'});
}

function setCleanUrl(query = ''){
  const next = location.pathname + query;
  history.replaceState(null, '', next);
}

function showQrChoice(){
  const qrChoice = $('#qrChoice');
  qrChoice?.classList.add('show');
  qrChoice?.setAttribute('aria-hidden', 'false');
  document.body.classList.add('qr-choice-active');
}

function hideQrChoice(){
  const qrChoice = $('#qrChoice');
  qrChoice?.classList.remove('show');
  qrChoice?.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('qr-choice-active');
}

function showInvitationMode(){
  document.body.classList.remove('memory-only');
  hideQrChoice();
  setCleanUrl('');
  resetInvitationGate();
}

function showMemoryOnlyMode(){
  hideQrChoice();
  document.body.classList.add('memory-only');
  document.documentElement.classList.remove('gate-locked');
  document.body.classList.remove('gate-locked');
  $('#inviteGate')?.classList.add('hide');
  closeMenu();
  setCleanUrl('?share=memories');
  setTimeout(() => $('#upload')?.scrollIntoView({behavior:'auto', block:'center'}), 0);
}

function initEntryMode(){
  const params = new URLSearchParams(location.search);
  if(params.get('share') === 'memories'){
    showMemoryOnlyMode();
    return;
  }
  if(params.get('qr') === '1'){
    showQrChoice();
  }
}

function openMenu(){
  $('#sideMenu')?.classList.add('open');
  document.body.classList.add('menu-open');
  $('#sideMenu')?.setAttribute('aria-hidden','false');
  $('#menuBtn')?.setAttribute('aria-expanded','true');
}
function closeMenu(){
  $('#sideMenu')?.classList.remove('open');
  document.body.classList.remove('menu-open');
  $('#sideMenu')?.setAttribute('aria-hidden','true');
  $('#menuBtn')?.setAttribute('aria-expanded','false');
}

function updateCountdown(){
  const daysNode = $('#days');
  const hoursNode = $('#hours');
  const minutesNode = $('#minutes');
  const secondsNode = $('#seconds');
  if(!daysNode || !hoursNode || !minutesNode || !secondsNode) return;

  const diff = Math.max(0, EVENT_DATE.getTime() - Date.now());
  const totalSeconds = Math.floor(diff / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  daysNode.textContent = String(days).padStart(3,'0');
  hoursNode.textContent = String(hours).padStart(2,'0');
  minutesNode.textContent = String(minutes).padStart(2,'0');
  secondsNode.textContent = String(seconds).padStart(2,'0');
}

function initReveal(){
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  $$('.reveal').forEach(section => {
    const parts = $$(':scope > .section-title, .card-soft, .story-card, .gallery-item, .location-card, .map-card, .final-card', section);
    parts.forEach((part, index) => part.style.setProperty('--reveal-delay', `${Math.min(index * 70, 520)}ms`));
  });
  if (reduce) return $$('.reveal').forEach(el => el.classList.add('in'));
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.classList.add('in');
        observer.unobserve(entry.target);
      }
    });
  }, {threshold: .13, rootMargin:'0px 0px -8% 0px'});
  $$('.reveal').forEach(el => observer.observe(el));
}

function initScroll(){
  const progress = $('#scrollProgress');
  const topbar = $('#topbar');
  const parallax = $$('.parallax');
  let ticking = false;
  const onFrame = () => {
    const max = document.documentElement.scrollHeight - innerHeight;
    const pct = max > 0 ? (scrollY / max) * 100 : 0;
    progress.style.width = pct + '%';
    topbar?.classList.toggle('scrolled', scrollY > 20);
    parallax.forEach(el => {
      const speed = Number(el.dataset.speed || 0.03);
      const rect = el.getBoundingClientRect();
      const offset = (rect.top - innerHeight / 2) * speed;
      el.style.transform = `translate3d(0, ${offset}px, 0)`;
    });
    ticking = false;
  };
  addEventListener('scroll', () => {
    if(!ticking){ requestAnimationFrame(onFrame); ticking = true; }
  }, {passive:true});
  onFrame();
}

function initPetals(){
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const canvas = $('#petalsCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const petals = Array.from({length: 24}, () => ({
    x: Math.random() * innerWidth,
    y: Math.random() * innerHeight,
    r: 4 + Math.random() * 8,
    vx: -0.2 + Math.random() * 0.4,
    vy: 0.3 + Math.random() * 0.7,
    rot: Math.random() * Math.PI,
    alpha: .12 + Math.random() * .18
  }));
  function resize(){ canvas.width = innerWidth * devicePixelRatio; canvas.height = innerHeight * devicePixelRatio; ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0); }
  resize(); addEventListener('resize', resize, {passive:true});
  function frame(){
    ctx.clearRect(0,0,innerWidth,innerHeight);
    petals.forEach(p => {
      p.x += p.vx; p.y += p.vy; p.rot += 0.01;
      if(p.y > innerHeight + 30){ p.y = -30; p.x = Math.random() * innerWidth; }
      if(p.x < -30) p.x = innerWidth + 30;
      ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.rot);
      ctx.beginPath(); ctx.ellipse(0,0,p.r,p.r*.6,0,0,Math.PI*2);
      ctx.fillStyle = `rgba(255,255,255,${p.alpha})`; ctx.fill();
      ctx.restore();
    });
    requestAnimationFrame(frame);
  }
  frame();
}

function initFlowerShower(){
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const layer = $('#flowerShower');
  if(!layer) return;
  const glyphs = ['✿', '❀', '✽', '✾', '✼'];
  const makeFlower = () => {
    const flower = document.createElement('span');
    const fromLeft = Math.random() > .5;
    const start = fromLeft ? -8 + Math.random() * 18 : 90 + Math.random() * 18;
    const drift = fromLeft
      ? 24 + Math.random() * 46
      : -(24 + Math.random() * 46);
    const size = 16 + Math.random() * (innerWidth > 760 ? 22 : 14);
    flower.className = `fall-flower${Math.random() > .82 ? ' gold' : ''}`;
    flower.textContent = glyphs[Math.floor(Math.random() * glyphs.length)];
    flower.style.setProperty('--start-x', `${start.toFixed(1)}vw`);
    flower.style.setProperty('--drift-x', `${drift.toFixed(1)}vw`);
    flower.style.setProperty('--flower-size', `${size.toFixed(1)}px`);
    flower.style.setProperty('--flower-duration', `${7.5 + Math.random() * 6}s`);
    flower.style.setProperty('--flower-delay', `${Math.random() * .45}s`);
    flower.style.setProperty('--flower-opacity', `${.38 + Math.random() * .32}`);
    flower.style.setProperty('--flower-rotate', `${Math.round((fromLeft ? 1 : -1) * (140 + Math.random() * 280))}deg`);
    layer.appendChild(flower);
    setTimeout(() => flower.remove(), 14000);
  };
  const initialCount = innerWidth > 760 ? 18 : 10;
  for(let index = 0; index < initialCount; index += 1) setTimeout(makeFlower, index * 180);
  setInterval(makeFlower, innerWidth > 760 ? 620 : 920);
}

function initGallery(){
  const chips = $$('.chips button');
  const galleryGrid = $('.gallery-grid');
  if (galleryGrid) {
    $$('.gallery-item', galleryGrid)
      .map(item => ({ item, sort: Math.random() }))
      .sort((a, b) => a.sort - b.sort)
      .forEach(({ item }) => galleryGrid.appendChild(item));
  }
  const items = $$('.gallery-item');
  if (chips.length) {
    chips.forEach(chip => chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const filter = chip.dataset.filter;
      items.forEach(item => item.classList.toggle('hidden', filter !== 'all' && item.dataset.cat !== filter));
    }));
  }

  const lightbox = $('#lightbox');
  const lightboxImg = $('#lightboxImg');
  const lightboxVideo = $('#lightboxVideo');
  const prevBtn = $('#lightboxPrev');
  const nextBtn = $('#lightboxNext');
  let activeIndex = 0;

  const showMedia = index => {
    activeIndex = (index + items.length) % items.length;
    const item = items[activeIndex];
    const isVideo = item.dataset.media === 'video';
    lightbox?.classList.toggle('media-video', isVideo);
    lightbox?.classList.toggle('media-image', !isVideo);
    if (isVideo) {
      lightboxImg.removeAttribute('src');
      lightboxVideo.src = item.dataset.src;
      lightboxVideo.play().catch(() => {});
    } else {
      const img = $('img', item);
      lightboxVideo.pause();
      lightboxVideo.removeAttribute('src');
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt;
    }
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');
  };

  items.forEach((item, index) => item.addEventListener('click', () => showMedia(index)));
  prevBtn?.addEventListener('click', () => showMedia(activeIndex - 1));
  nextBtn?.addEventListener('click', () => showMedia(activeIndex + 1));
  $('#lightboxClose')?.addEventListener('click', closeLightbox);
  lightbox?.addEventListener('click', e => { if(e.target === lightbox) closeLightbox(); });
  addEventListener('keydown', e => {
    if (!lightbox?.classList.contains('open')) return;
    if(e.key === 'Escape') closeLightbox();
    if(e.key === 'ArrowLeft') showMedia(activeIndex - 1);
    if(e.key === 'ArrowRight') showMedia(activeIndex + 1);
  });
  function closeLightbox(){
    lightboxVideo?.pause();
    lightboxImg?.removeAttribute('src');
    lightboxVideo?.removeAttribute('src');
    lightbox?.classList.remove('open', 'media-image', 'media-video');
    lightbox?.setAttribute('aria-hidden', 'true');
  }
}

function updateFileCount(){
  const input = $('#memoryFiles');
  const fileCount = $('#fileCount');
  if(!input || !fileCount) return;
  const files = selectedMemoryFiles.length ? selectedMemoryFiles : [...(input.files || [])];
  const count = files.length;
  fileCount.textContent = count ? `${count} ${t('fileSelected')}` : t('noFile');
}

function isPhotoFile(file){
  const name = file.name.toLowerCase();
  return file.type.startsWith('image/') || /\.(png|jpe?g|gif|webp|heic|heif)$/.test(name);
}

function isVideoFile(file){
  const name = file.name.toLowerCase();
  return file.type.startsWith('video/') || /\.(mp4|webm|mov|avi|mkv)$/.test(name);
}

function syncMemoryInput(input){
  const dt = new DataTransfer();
  selectedMemoryFiles.forEach(file => dt.items.add(file));
  input.files = dt.files;
  updateFileCount();
}

function addMemoryFiles(input, files){
  const next = [...selectedMemoryFiles];
  let skipped = false;

  Array.from(files).forEach(file => {
    const duplicate = next.some(existing =>
      existing.name === file.name &&
      existing.size === file.size &&
      existing.lastModified === file.lastModified
    );
    if(duplicate) return;

    if(isPhotoFile(file) || isVideoFile(file)){
      next.push(file);
      return;
    }

    skipped = true;
  });

  selectedMemoryFiles = next;
  syncMemoryInput(input);
  if(skipped) toast(t('invalidFile'));
}

function initUpload(){
  const form = $('#memoryUploadForm');
  const input = $('#memoryFiles');
  const dropZone = $('#dropZone');
  const list = $('#uploadList');
  const thanks = $('#uploadThanks');
  if(!form || !input || !dropZone) return;

  input.addEventListener('change', () => {
    if(input.files?.length) addMemoryFiles(input, input.files);
    else syncMemoryInput(input);
    thanks?.classList.remove('show');
  });

  form.addEventListener('submit', async e => {
    e.preventDefault();
    list.innerHTML = '';
    thanks?.classList.remove('show');
    const files = [...input.files];
    if(!files.length){ toast(t('noFile')); return; }

    const rows = files.map(file => {
      const row = document.createElement('div');
      row.className = 'upload-row';
      row.innerHTML = `<strong>${file.name}</strong><progress max="100" value="0"></progress><small>0%</small>`;
      list.appendChild(row);
      return {progress: $('progress', row), small: $('small', row)};
    });

    if(REAL_UPLOAD_ENABLED){
      const failedFiles = [];
      const guestName = new FormData(form).get('guestName') || 'guest';

      for(const [index, file] of files.entries()){
        const {progress, small} = rows[index];
        const data = new FormData();
        data.append('guestName', guestName);
        data.append('memories', file);

        try{
          await uploadWithProgress(data, percent => {
            progress.value = percent;
            small.textContent = `${percent}%`;
          });
          progress.value = 100;
          small.textContent = t('uploadDone');
        }catch(err){
          const message = err.message || t('uploadFailed');
          small.textContent = message;
          failedFiles.push(file);
        }
      }

      if(!failedFiles.length){
        toast(t('uploadAlert'));
        form.reset();
        selectedMemoryFiles = [];
        updateFileCount();
        thanks?.classList.add('show');
      }else{
        selectedMemoryFiles = failedFiles;
        syncMemoryInput(input);
        const retry = document.createElement('button');
        retry.className = 'upload-retry';
        retry.type = 'button';
        retry.textContent = t('retryUpload');
        retry.addEventListener('click', () => {
          retry.remove();
          form.requestSubmit();
        });
        list.appendChild(retry);
        toast(t('uploadFailed'));
      }
      return;
    }

    for(const {progress, small} of rows){
      await fakeProgress(progress, small);
      small.textContent = t('uploadDone');
    }
    toast(t('uploadAlert'));
    form.reset();
    selectedMemoryFiles = [];
    updateFileCount();
    thanks?.classList.add('show');
  });
}

function uploadWithProgress(data, onProgress){
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', UPLOAD_ENDPOINT);
    xhr.upload.addEventListener('progress', event => {
      if(!event.lengthComputable) return;
      const percent = Math.max(5, Math.min(95, Math.round((event.loaded / event.total) * 95)));
      onProgress(percent);
    });
    xhr.addEventListener('load', () => {
      let payload = {};
      try{
        payload = xhr.responseText ? JSON.parse(xhr.responseText) : {};
      }catch(err){
        reject(new Error(t('uploadResponse')));
        return;
      }
      if(xhr.status >= 200 && xhr.status < 300 && payload.success !== false){
        resolve(payload);
        return;
      }
      reject(new Error(normalizeUploadError(payload.error)));
    });
    xhr.addEventListener('error', () => reject(new Error(t('uploadConnection'))));
    xhr.addEventListener('timeout', () => reject(new Error(t('uploadFailed'))));
    xhr.timeout = 1000 * 60 * 20;
    onProgress(5);
    xhr.send(data);
  });
}

function normalizeUploadError(error){
  if(error === 'No files provided.') return t('noFile');
  if(error === 'Invalid file type.') return t('invalidFile');
  if(error === 'Upload exceeded the maximum allowed size.') return t('fileTooLarge');
  return error || t('uploadFailed');
}

function fakeProgress(progress, label){
  return new Promise(resolve => {
    let value = 0;
    const timer = setInterval(() => {
      value += 8 + Math.random() * 12;
      if(value >= 100){ value = 100; clearInterval(timer); resolve(); }
      progress.value = value;
      label.textContent = `${Math.round(value)}%`;
    }, 80);
  });
}

function initForms(){
  $('#rsvpForm')?.addEventListener('submit', async e => {
    e.preventDefault();
    const form = e.currentTarget;
    try{
      const response = await fetch('/api/rsvp', {method:'POST', body:new FormData(form)});
      if(!response.ok) throw new Error('RSVP failed');
      toast(t('rsvpAlert'));
      form.reset();
    }catch(err){
      toast(t('rsvpError'));
    }
  });
}

function initQr(){
  const urlEl = $('#inviteUrl');
  if(urlEl) urlEl.textContent = INVITE_URL;
  $('#copyInviteLink')?.addEventListener('click', async () => {
    try{
      await navigator.clipboard.writeText(INVITE_URL);
      toast(t('linkCopied'));
    }catch{ toast(INVITE_URL); }
  });
  $('#downloadCalendar')?.addEventListener('click', () => {
    const ics = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//FikrieSafak//Engagement//EN',
      'BEGIN:VEVENT',
      'UID:safak-fikrie-engagement-20260926@example.com',
      'DTSTAMP:20260616T000000Z',
      'DTSTART:20260926T160000Z',
      'DTEND:20260926T200000Z',
      'SUMMARY:Fikrie & Şafak Engagement',
      'LOCATION:1972 43, 2930 Valkosel, Bulgaria',
      'DESCRIPTION:Fikrie & Şafak engagement invitation. ' + INVITE_URL,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');
    const blob = new Blob([ics], {type:'text/calendar;charset=utf-8'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'safak-fikrie-engagement.ics';
    a.click();
    URL.revokeObjectURL(a.href);
    toast(t('calendarDownloaded'));
  });
}

let audioStarted = false;
function startSiteAudio(){
  const audio = $('#siteAudio');
  if(!audio) return Promise.resolve();
  audio.volume = audio.volume || .45;
  audio.muted = false;
  return audio.play().then(() => {
    audioStarted = true;
    updateAudioControl();
  }).catch(() => {
    updateAudioControl();
  });
}

function updateAudioControl(){
  const audio = $('#siteAudio');
  const toggle = $('#audioToggle');
  if(!audio || !toggle) return;
  const isSilent = audio.paused || audio.muted || audio.volume === 0;
  toggle.textContent = isSilent ? '♪' : '♫';
  toggle.title = isSilent ? t('audioOff') : t('audioOn');
  toggle.setAttribute('aria-label', t('audioToggleLabel'));
  toggle.setAttribute('aria-pressed', String(!isSilent));
}

function initAudio(){
  const audio = $('#siteAudio');
  const toggle = $('#audioToggle');
  if(!audio) return;

  audio.volume = .45;
  audio.muted = false;
  updateAudioControl();

  toggle?.addEventListener('click', () => {
    if(audio.paused){
      startSiteAudio();
      return;
    }
    audio.pause();
    audio.muted = false;
    updateAudioControl();
  });

  audio.addEventListener('play', updateAudioControl);
  audio.addEventListener('pause', updateAudioControl);
  audio.addEventListener('volumechange', updateAudioControl);
}

function bindBaseEvents(){
  $('#inviteGate')?.addEventListener('click', e => {
    if(e.target.closest('[data-lang], .gate-language')) return;
    openInvitation();
  });
  $('#openInvite')?.addEventListener('click', e => {
    e.stopPropagation();
    openInvitation();
  });
  $('#openInvite')?.addEventListener('keydown', e => {
    if(e.key !== 'Enter' && e.key !== ' ') return;
    e.preventDefault();
    openInvitation();
  });
  $('#menuBtn')?.addEventListener('click', openMenu);
  $('#menuClose')?.addEventListener('click', closeMenu);
  $('#sideMenu')?.addEventListener('click', e => { if(e.target.id === 'sideMenu') closeMenu(); });
  $$('.side-menu a').forEach(a => a.addEventListener('click', closeMenu));
  $$('.logo-reopen').forEach(link => link.addEventListener('click', e => {
    e.preventDefault();
    closeMenu();
    resetInvitationGate();
  }));
  $$('[data-lang]').forEach(btn => btn.addEventListener('click', e => {
    e.stopPropagation();
    applyLanguage(btn.dataset.lang);
  }));
  $('#qrOpenInvite')?.addEventListener('click', showInvitationMode);
  $('#qrShareMemories')?.addEventListener('click', showMemoryOnlyMode);
}

bindBaseEvents();
applyLanguage(currentLang);
initEntryMode();
updateCountdown();
setInterval(updateCountdown, 1000);
initReveal();
initScroll();
initPetals();
initFlowerShower();
initGallery();
initUpload();
initForms();
initQr();
initAudio();

