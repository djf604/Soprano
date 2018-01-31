var loadingPhrases = [
    "640K ought to be enough for anybody",
    "the reagents are still shipping",
    "the bits are breeding",
    "we're building the dots as fast as we can",
    "would you prefer chicken, steak, or tofu?",
    "and enjoy the elevator music",
    "while the little elves work on your data",
    "a few bits tried to escape, but we caught them",
    "and dream of faster computers",
    "would you like fries with that?",
    "checking the gravitational constant in your locale",
    "go ahead -- hold your breath",
    "at least you're not on hold",
    "hum something loud while others stare",
    "you're not in Kansas any more",
    "the server is powered by a lemon and two electrodes",
    "we love you just the way you are",
    "we're testing your patience",
    "as if you had any other choice",
    "don't think of purple hippos",
    "follow the white rabbit",
    "why don't you order a sandwich?",
    "while the satellite moves into position",
    "the bits are flowing slowly today",
    "it's still faster than you could draw it"
];

function getLoadingPhrase() {
    var randomIndex = Math.floor(Math.random() * loadingPhrases.length);
    document.write(loadingPhrases[randomIndex]);
}