window.onload = function() {
    if (location.href == "http://localhost:5000/main") {
        tablazatFeltoltese();
    }
}

function napokSzamaEgyHonapban(ev,honap) {
    const datum = new Date(ev, honap, 0);
    return datum.getDate();
}

var balra_szamlalo = 0;
var jobbra_szamlalo = 0;

function Balra() {
    balra_szamlalo--;
    tablazatFeltoltese();
}

function Jobbra() {
    jobbra_szamlalo++;
    tablazatFeltoltese();
}

var megadottHonapIndexje = 0;
var megadottEv = 0;
var megadottNap = 0;
var honapok = [];

function Napok() {
    honapok = ["Január", "Február", "Március", "Április", "Május", "Június", "Július", "Augusztus", "Szeptember", "Október", "November", "December"];

    const datum = new Date();
    var jelenlegiEv = datum.getFullYear();
    var jelenlegiHonap = datum.getMonth() + 1 + balra_szamlalo + jobbra_szamlalo;

    const datum2 = new Date(jelenlegiEv, jelenlegiHonap, 0);
    const napokAJelenlegiHonapban = datum2.getDate();
    megadottHonapIndexje = datum2.getMonth();
    megadottEv = datum2.getFullYear();

    document.getElementById("tablazat-fejlec-ev").innerHTML = "";
    document.getElementById("tablazat-fejlec-ev").innerHTML += `${megadottEv}.`;
    document.getElementById("tablazat-fejlec-honap").innerHTML = "";
    document.getElementById("tablazat-fejlec-honap").innerHTML += ` ${honapok[megadottHonapIndexje]}\n`;

    megadottNap = napokAJelenlegiHonapban;

    return napokAJelenlegiHonapban;
}

function erzesBe(status) {
    var ev = megadottEv;
    var honap = megadottHonapIndexje;
    var nap = new Date();
    if (ev == undefined || honap == undefined || nap.getDate() == undefined || status == undefined) {
        return;
    }
    var kuldeni = JSON.stringify({
        year : ev,
        month : honap,
        day: nap.getDate(),
        status: status
    });
    var objektum = new XMLHttpRequest();
    objektum.onreadystatechange = function() {
        if (objektum.readyState === 4 && objektum.status === 400){
            var hiba = JSON.parse(this.responseText);
            alert(hiba.error);
        }
    }
    objektum.open("POST", "http://localhost:5000/erzes", true);
    objektum.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    objektum.send(kuldeni);

    setTimeout(()=>{
        adatbazisAdatok();
    }, 50);
}

function adatbazisAdatok() {
    var objektum = new XMLHttpRequest();
    objektum.onreadystatechange = function() {
        if (objektum.readyState === 4 && objektum.status === 200) {
            try {
                var adatbazis = JSON.parse(this.responseText);
                naptarFeltolt(adatbazis);
            } catch (error) {
                console.log("JSON Parsing Error:", error);
            }
        }
    }
    objektum.open("GET", "http://localhost:5000/erzeski", true);
    objektum.setRequestHeader("Accept", "application/json");
    objektum.send();
}

function naptarFeltolt(adatbazis){
    const bruno_kepek = ["bruno_atlagos.png", "bruno_boldog.png", "bruno_faradt.png", "bruno_duhos.png", "bruno_izgatott.png", "bruno_szerelmes.png", "bruno_szomoru.png", "bruno_unott.png", "bruno_visszahuzodo.png"];
    var mainap = new Date();
    if (adatbazis.length != 0) {
        if (adatbazis[adatbazis.length - 1].year == mainap.getFullYear() && adatbazis[adatbazis.length - 1].month == mainap.getMonth() && adatbazis[adatbazis.length - 1].day == mainap.getDate()) {
            document.getElementById("segito").src = "";
            document.getElementById("segito").src = "static/Bruno_egylufi/" + bruno_kepek[adatbazis[adatbazis.length - 1].status];
            document.getElementById("segito").classList = "";
            document.getElementById("segito").classList += "top";
            document.getElementById("my-image-map").innerHTML = "";
        }
    }

    var statuszok = ["atlagos.png", "boldog.png", "faradt.png", "haragos.png", "izgatott.png", "szerelmes.png", "szomoru.png", "unott.png", "visszahuzodo.png"];
    var alt_es_title_szovegek = ["Átlagos", "Boldog", "Fáradt", "Haragos", "Izgatott", "Szerelmes", "Szomorú", "Unott", "Visszahúzódó"];
    for (let i = 0; i < adatbazis.length; i++) { 
        if (megadottEv == adatbazis[i].year && megadottHonapIndexje == adatbazis[i].month) {
            for (let j = 1; j <= megadottNap; j++) {
                if (j == adatbazis[i].day) {
                    document.getElementById(`${j}-nap`).src = "static/images/" + statuszok[adatbazis[i].status];
                    document.getElementById(`${j}-nap`).title = alt_es_title_szovegek[adatbazis[i].status];
                    document.getElementById(`${j}-nap`).alt = alt_es_title_szovegek[adatbazis[i].status];
                    document.getElementById(`${j}-p`).innerHTML = "<p>" + alt_es_title_szovegek[adatbazis[i].status]+ "</p>";
                    break;
                }
            }
        }
    }
}

function tablazatFeltoltese() {
    adatbazisAdatok();
    const hetek = ["elso-het", "masodik-het", "harmadik-het", "negyedik-het", "otodik-het"];

    document.getElementById(hetek[0]).innerHTML = "";
    document.getElementById(hetek[1]).innerHTML = "";
    document.getElementById(hetek[2]).innerHTML = "";
    document.getElementById(hetek[3]).innerHTML = "";
    document.getElementById(hetek[4]).innerHTML = "";
    
    var napokSzama = Napok();
    var napSzamlalo = 0;
    for (let i = 0; i < napokSzama; i++) {
        if (napSzamlalo < 7) {
            document.getElementById(hetek[0]).innerHTML += `<td><p class="naptar" id="${i + 1}-naptarnap">${i + 1}.</p><img id="${i + 1}-nap"><p id=${i + 1}-p></p></td>\n`;
        }
        else if (napSzamlalo < 14) {
            document.getElementById(hetek[1]).innerHTML += `<td><p class="naptar" id="${i + 1}-naptarnap">${i + 1}.</p><img id="${i + 1}-nap"><p id=${i + 1}-p></p></td>\n`;
        }
        else if (napSzamlalo < 21) {
            document.getElementById(hetek[2]).innerHTML += `<td><p class="naptar" id="${i + 1}-naptarnap">${i + 1}.</p><img id="${i + 1}-nap"><p id=${i + 1}-p></p></td>\n`;
        }
        else if (napSzamlalo < 28) {
            document.getElementById(hetek[3]).innerHTML += `<td><p class="naptar" id="${i + 1}-naptarnap">${i + 1}.</p><img id="${i + 1}-nap"><p id=${i + 1}-p></p></td>\n`;
        }
        else {
            document.getElementById(hetek[4]).innerHTML += `<td><p class="naptar" id="${i + 1}-naptarnap">${i + 1}.</p><img id="${i + 1}-nap"><p id=${i + 1}-p></p></td>\n`;
        }

        napSzamlalo++;
    }
    var mainap = new Date()
    if (megadottHonapIndexje == mainap.getMonth()) {
        document.getElementById(mainap.getDate() + "-naptarnap").classList.remove("naptar");
        document.getElementById(mainap.getDate() + "-naptarnap").classList.add("naptar-kivalasztott");
    }
}