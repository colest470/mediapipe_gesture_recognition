let nums = [3,2,3];
let target = 6;

var twoSum = function(nums, target) {
    const arrLen = nums.length;

    for(let i = 0; i < arrLen; i++){
        let sum = 0;

        sum = nums[i] + nums[i + 1];

        let returnArr = [];

        if(target === sum){
            returnArr.push(i);
            returnArr.push(i + 1);

            return returnArr || [];
        } else {
            if(i == 0 || i == 1){
                continue;
            }

            for (let k = i-2; k >= 0; k=k-1) {
                console.log(k, i);
                sum = nums[i] + nums[k];

                console.log(sum);

                if(target === sum) {
                    returnArr.push(k);
                    returnArr.push(i);

                    return returnArr;
                }
            }
        }

    }

    return [];
};

console.log(twoSum(nums, target));