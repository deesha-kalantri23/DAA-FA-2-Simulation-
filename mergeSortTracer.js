/**
 * mergeSortTracer.js
 * Manual Merge Sort implementation with detailed step-by-step state tracking
 * for educational visualization in the browser.
 * 
 * Academic focus:
 * - Divide and Conquer paradigm
 * - Descending order sorting based on Water Level (highest risk evacuated first)
 * - NO use of built-in sort()
 * - Exact deterministic parity with merge_sort.py and merge_sort.cpp
 */

export class AreaRecord {
  constructor(areaId, name, waterLevel, population) {
    this.areaId = areaId;
    this.name = name;
    this.waterLevel = parseFloat(waterLevel);
    this.population = parseInt(population, 10);
  }

  getPriority() {
    if (this.waterLevel >= 7.5) return "CRITICAL";
    if (this.waterLevel >= 6.0) return "HIGH";
    if (this.waterLevel >= 4.0) return "MEDIUM";
    return "LOW";
  }

  clone() {
    return new AreaRecord(this.areaId, this.name, this.waterLevel, this.population);
  }
}

export class AlgorithmState {
  constructor({
    stepId,
    opType, // "DIVIDE", "COMPARE", "SELECT", "MERGE_ITEM", "MERGE_DONE"
    depth,
    activeRange, // [startIdx, endIdx]
    leftSub = [],
    rightSub = [],
    currLeftIdx = null,
    currRightIdx = null,
    compLeftVal = null,
    compRightVal = null,
    selectedItem = null,
    comparisonText = "",
    whyText = "",
    mergedBuffer = [],
    arraySnapshot = [],
    comparisonsSoFar = 0,
    mergesSoFar = 0,
    explanation = ""
  }) {
    this.stepId = stepId;
    this.opType = opType;
    this.depth = depth;
    this.activeRange = activeRange;
    this.leftSub = leftSub.map(item => item ? item.clone() : null);
    this.rightSub = rightSub.map(item => item ? item.clone() : null);
    this.currLeftIdx = currLeftIdx;
    this.currRightIdx = currRightIdx;
    this.compLeftVal = compLeftVal;
    this.compRightVal = compRightVal;
    this.selectedItem = selectedItem ? selectedItem.clone() : null;
    this.comparisonText = comparisonText;
    this.whyText = whyText;
    this.mergedBuffer = mergedBuffer.map(item => item ? item.clone() : null);
    this.arraySnapshot = arraySnapshot.map(item => item ? item.clone() : null);
    this.comparisonsSoFar = comparisonsSoFar;
    this.mergesSoFar = mergesSoFar;
    this.explanation = explanation;
  }
}

export class TreeNode {
  constructor(nodeId, start, end, depth, elements) {
    this.nodeId = nodeId;
    this.start = start;
    this.end = end;
    this.depth = depth;
    this.elements = elements.map(e => e.clone());
    this.leftChild = null;
    this.rightChild = null;
    this.state = "PENDING";
  }
}

export class MergeSortTracer {
  constructor(initialData) {
    this.originalData = initialData.map(e => e.clone());
    this.workArray = initialData.map(e => e.clone());
    this.timeline = [];
    this.comparisonsCount = 0;
    this.mergesCount = 0;
    this.stepCounter = 0;
    this.maxDepth = 0;
    this.treeRoot = null;
    this._treeNodeCounter = 0;

    this._executeAndTrace();
  }

  _createTree(start, end, depth) {
    this._treeNodeCounter += 1;
    const node = new TreeNode(
      this._treeNodeCounter,
      start,
      end,
      depth,
      this.workArray.slice(start, end + 1)
    );
    if (depth > this.maxDepth) {
      this.maxDepth = depth;
    }

    if (start < end) {
      const mid = Math.floor((start + end) / 2);
      node.leftChild = this._createTree(start, mid, depth + 1);
      node.rightChild = this._createTree(mid + 1, end, depth + 1);
    }
    return node;
  }

  _executeAndTrace() {
    this.treeRoot = this._createTree(0, this.workArray.length - 1, 0);
    this._mergeSortRecursive(0, this.workArray.length - 1, 0);
  }

  _mergeSortRecursive(start, end, depth) {
    if (start >= end) {
      return;
    }

    const mid = Math.floor((start + end) / 2);

    // 1. DIVIDE EVENT
    const leftSlice = this.workArray.slice(start, mid + 1);
    const rightSlice = this.workArray.slice(mid + 1, end + 1);

    this.stepCounter += 1;
    this.timeline.push(
      new AlgorithmState({
        stepId: this.stepCounter,
        opType: "DIVIDE",
        depth: depth,
        activeRange: [start, end],
        leftSub: leftSlice,
        rightSub: rightSlice,
        arraySnapshot: this.workArray,
        comparisonsSoFar: this.comparisonsCount,
        mergesSoFar: this.mergesCount,
        explanation: `DIVIDE: Split subarray of ${end - start + 1} areas into [${start}..${mid}] (${leftSlice.length} items) and [${mid + 1}..${end}] (${rightSlice.length} items).`,
        whyText: "Divide and Conquer breaks the problem into subproblems until single-element arrays remain."
      })
    );

    // 2. RECURSE LEFT
    this._mergeSortRecursive(start, mid, depth + 1);

    // 3. RECURSE RIGHT
    this._mergeSortRecursive(mid + 1, end, depth + 1);

    // 4. MERGE
    this._merge(start, mid, end, depth);
  }

  _merge(start, mid, end, depth) {
    const leftCopy = this.workArray.slice(start, mid + 1).map(x => x.clone());
    const rightCopy = this.workArray.slice(mid + 1, end + 1).map(x => x.clone());

    const mergedBuffer = [];
    let i = 0;
    let j = 0;

    while (i < leftCopy.length && j < rightCopy.length) {
      const leftItem = leftCopy[i];
      const rightItem = rightCopy[j];

      this.comparisonsCount += 1;
      const leftVal = leftItem.waterLevel;
      const rightVal = rightItem.waterLevel;

      // COMPARE STEP
      this.stepCounter += 1;
      this.timeline.push(
        new AlgorithmState({
          stepId: this.stepCounter,
          opType: "COMPARE",
          depth: depth,
          activeRange: [start, end],
          leftSub: leftCopy,
          rightSub: rightCopy,
          currLeftIdx: i,
          currRightIdx: j,
          compLeftVal: leftVal,
          compRightVal: rightVal,
          comparisonText: `${leftItem.name} (${leftVal.toFixed(1)}m) vs ${rightItem.name} (${rightVal.toFixed(1)}m)`,
          whyText: "Comparing flood levels. In descending sort, the area with the HIGHER water level has highest evacuation urgency.",
          mergedBuffer: mergedBuffer,
          arraySnapshot: this.workArray,
          comparisonsSoFar: this.comparisonsCount,
          mergesSoFar: this.mergesCount,
          explanation: `COMPARE: ${leftItem.areaId} (${leftVal}m) vs ${rightItem.areaId} (${rightVal}m).`
        })
      );

      let chosen;
      let reason;
      if (leftVal >= rightVal) {
        chosen = leftItem;
        reason = `${leftVal.toFixed(1)}m >= ${rightVal.toFixed(1)}m: ${leftItem.name} has higher flood level, placing it first.`;
        i += 1;
      } else {
        chosen = rightItem;
        reason = `${rightVal.toFixed(1)}m > ${leftVal.toFixed(1)}m: ${rightItem.name} has higher flood level, placing it first.`;
        j += 1;
      }

      mergedBuffer.push(chosen);

      // SELECT & INSERT STEP
      this.stepCounter += 1;
      this.timeline.push(
        new AlgorithmState({
          stepId: this.stepCounter,
          opType: "SELECT",
          depth: depth,
          activeRange: [start, end],
          leftSub: leftCopy,
          rightSub: rightCopy,
          currLeftIdx: chosen === leftItem ? i - 1 : i,
          currRightIdx: chosen === rightItem ? j - 1 : j,
          selectedItem: chosen,
          comparisonText: `Selected ${chosen.name} (${chosen.waterLevel.toFixed(1)}m)`,
          whyText: reason,
          mergedBuffer: mergedBuffer,
          arraySnapshot: this.workArray,
          comparisonsSoFar: this.comparisonsCount,
          mergesSoFar: this.mergesCount,
          explanation: `SELECT: Added ${chosen.areaId} (${chosen.name}) to merged list.`
        })
      );
    }

    // Collect remaining left
    while (i < leftCopy.length) {
      const remItem = leftCopy[i];
      mergedBuffer.push(remItem);
      i += 1;
      this.stepCounter += 1;
      this.timeline.push(
        new AlgorithmState({
          stepId: this.stepCounter,
          opType: "MERGE_ITEM",
          depth: depth,
          activeRange: [start, end],
          leftSub: leftCopy,
          rightSub: rightCopy,
          selectedItem: remItem,
          comparisonText: `Append remaining: ${remItem.name} (${remItem.waterLevel.toFixed(1)}m)`,
          whyText: "Right subarray exhausted. Appending remaining sorted elements from left half.",
          mergedBuffer: mergedBuffer,
          arraySnapshot: this.workArray,
          comparisonsSoFar: this.comparisonsCount,
          mergesSoFar: this.mergesCount,
          explanation: `COLLECT: Appended remaining ${remItem.areaId} to buffer.`
        })
      );
    }

    // Collect remaining right
    while (j < rightCopy.length) {
      const remItem = rightCopy[j];
      mergedBuffer.push(remItem);
      j += 1;
      this.stepCounter += 1;
      this.timeline.push(
        new AlgorithmState({
          stepId: this.stepCounter,
          opType: "MERGE_ITEM",
          depth: depth,
          activeRange: [start, end],
          leftSub: leftCopy,
          rightSub: rightCopy,
          selectedItem: remItem,
          comparisonText: `Append remaining: ${remItem.name} (${remItem.waterLevel.toFixed(1)}m)`,
          whyText: "Left subarray exhausted. Appending remaining sorted elements from right half.",
          mergedBuffer: mergedBuffer,
          arraySnapshot: this.workArray,
          comparisonsSoFar: this.comparisonsCount,
          mergesSoFar: this.mergesCount,
          explanation: `COLLECT: Appended remaining ${remItem.areaId} to buffer.`
        })
      );
    }

    // Copy back to workArray
    this.mergesCount += 1;
    for (let k = 0; k < mergedBuffer.length; k++) {
      this.workArray[start + k] = mergedBuffer[k].clone();
    }

    this.stepCounter += 1;
    this.timeline.push(
      new AlgorithmState({
        stepId: this.stepCounter,
        opType: "MERGE_DONE",
        depth: depth,
        activeRange: [start, end],
        leftSub: leftCopy,
        rightSub: rightCopy,
        mergedBuffer: mergedBuffer,
        arraySnapshot: this.workArray,
        comparisonsSoFar: this.comparisonsCount,
        mergesSoFar: this.mergesCount,
        explanation: `MERGE COMPLETE: Subarray [${start}..${end}] (${mergedBuffer.length} items) is now sorted descending.`,
        whyText: "Both sorted halves have been merged into a single sorted subarray."
      })
    );
  }

  getFinalSorted() {
    return this.workArray.map(x => x.clone());
  }
}

export const INITIAL_FLOOD_AREAS = [
  new AreaRecord("A01", "Shivaji Nagar", 2.5, 850),
  new AreaRecord("A02", "Kothrud", 5.8, 1240),
  new AreaRecord("A03", "Viman Nagar", 3.2, 670),
  new AreaRecord("A04", "Hinjewadi", 7.1, 1580),
  new AreaRecord("A05", "Wakad", 4.6, 920),
  new AreaRecord("A06", "Baner", 6.3, 1430),
  new AreaRecord("A07", "Kharadi", 3.9, 760),
  new AreaRecord("A08", "Hadapsar", 8.2, 1890),
  new AreaRecord("A09", "Aundh", 2.8, 540),
  new AreaRecord("A10", "Pimpri", 6.9, 1720),
  new AreaRecord("A11", "Chinchwad", 5.1, 1150),
  new AreaRecord("A12", "Bhosari", 7.6, 1640),
  new AreaRecord("A13", "Dhankawadi", 4.2, 810),
  new AreaRecord("A14", "Katraj", 6.1, 1320),
  new AreaRecord("A15", "Warje", 3.5, 690),
  new AreaRecord("A16", "Lohegaon", 5.5, 980),
  new AreaRecord("A17", "Yerawada", 7.9, 1810),
  new AreaRecord("A18", "Dapodi", 4.8, 1050),
  new AreaRecord("A19", "Swargate", 6.5, 1370),
  new AreaRecord("A20", "Camp", 3.7, 620),
];
