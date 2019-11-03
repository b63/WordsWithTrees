const RADIANS = Math.PI/180;

function rand(high, low) {
    high = high || 1;
    low = low || -high;

    let range = Math.abs(high - low);
    return range * (Math.random()-0.5) + (low+high)/2.0;
}

// from https://stackoverflow.com/questions/25582882/javascript-math-random-normal-distribution-gaussian-bell-curve
function randn_bm() {
    let u = 0, v = 0;
    while(u === 0) u = Math.random(); //Converting [0,1) to (0,1)
    while(v === 0) v = Math.random();
    return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
}

function process_sparse(f, timeout) {
    const inner = function(resolve, reject){
        let stop = false;
        const complete = function() {
            stop = true;
            resolve(arguments);
        };

        const quit = function() {
            stop = true;
            reject(arguments);
        };

        const process = function() {
            if (!stop) {
                f(complete, quit);
                window.setTimeout(process, timeout);
            }
        };
        process();
    };

    return new Promise(inner);
}
