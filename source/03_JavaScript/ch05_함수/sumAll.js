// function sumAll() {
//     if (arguments.length === 0) {
//         return -999;
//     } else {
//         let sum = 0;
//         for (let i = 0; i < arguments.length; i++) {
//             sum += arguments[i];
//         }
//         return sum;
//     }
// }

// 선생님 버전
function sumAll() {
    var result = 0;
    if (arguments.length==0) {
        result = -999;
    } else {
        for (var data of arguments) {
            result += data;
        }
    }
    return result;
}


console.log(sumAll());
console.log(sumAll(1, 2));
console.log(sumAll(1, 2, 3, 4, 5));