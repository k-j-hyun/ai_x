class Student {
    constructor(name, kor, mat, eng, sci) {
        this.name = name;
        this.kor = kor;
        this.mat = mat;
        this.eng = eng;
        this.sci = sci;
    }
    getSum() {
        return this.kor + this.mat + this.eng + this.sci;
    }
    getAvg() {
            return this.getSum() / 4;
    }
    toString() {
        return 'name:' + this.name +
                ' kor:' + this.kor +
                ' mat:' + this.mat +
                ' eng:' + this.eng +
                ' sci:' + this.sci +
                ' sum:' + this.getSum() +
                ' avg:' + this.getAvg();
    }
} // class

var hong = new Student('홍', 90, 80, 55, 40);
console.log(hong.toString()); // 템플릿 리터럴에서 자동 호출
console.log(`${hong}`);