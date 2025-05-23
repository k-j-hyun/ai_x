Date.prototype.getIntervalDay = function(otherday) {
    //this와 otherday 사이의 날짜 수를 return
    //now.getIntervalDay(openday): this가 now, otherday가 openday
    //openday.getIntervalDay(now): this가 openday, otherday가 now
    // if (this > otherday) {
    //     var intervalMilliSec = this.getTime() - otherday.getTime();
    // } else {
    //     var intervalMilliSec = otherday.getTime() - this.getTime();
    // }

    // var intervalMilliSec = (this > otherday) ?
    //     (this.getTime() - otherday.getTime()) : (otherday.getTime() - this.getTime());

    var intervalMilliSec = Math.abs(this.getTime() - otherday.getTime());
    let day = intervalMilliSec / (1000*60*60*24);
    return Math.trunc(day); // Math.trunc(내림) Math.round(반올림) Math.ceil(올림)
};
//test
// let now = new Date();
// let openday = new Date(2025, 3, 7, 9, 30);
// console.log(now.getIntervalDay(openday), '일');
// console.log(openday.getIntervalDay(now), '일');



    //  function getDDay(targetDateStr) {}
//   const today = new Date();
//     const targetDate = new Date(targetDateStr);
    // 시, 분, 초, 밀리초 제거 → 날짜만 비교
//     today.setHours(0, 0, 0, 0);
//     targetDate.setHours(0, 0, 0, 0);

//     const diffTime = targetDate - today;
//     const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

//     if (diffDays > 0) {
//         return `D-${diffDays}`;
//     } else if (diffDays === 0) {
//         return 'D-Day';
//     } else {
//         return `D+${Math.abs(diffDays)}`;
//     }
// }