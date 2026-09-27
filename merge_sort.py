"""
merge_sort.py
Manual Merge Sort implementation with detailed step-by-step state tracking
for educational visualization in Pygame.

Academic focus:
- Divide and Conquer paradigm
- Descending order sorting based on Water Level (highest risk evacuated first)
- NO use of sort() or sorted() built-ins
"""

from typing import List, Dict, Any, Optional
import copy


class AreaRecord:
    """Represents a single flood area record."""
    def __init__(self, area_id: str, name: str, water_level: float, population: int):
        self.area_id = area_id
        self.name = name
        self.water_level = float(water_level)
        self.population = int(population)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.area_id,
            "name": self.name,
            "water_level": self.water_level,
            "population": self.population,
            "priority": self.get_priority(),
        }

    def get_priority(self) -> str:
        if self.water_level >= 7.5:
            return "CRITICAL"
        elif self.water_level >= 6.0:
            return "HIGH"
        elif self.water_level >= 4.0:
            return "MEDIUM"
        else:
            return "LOW"

    def __repr__(self) -> str:
        return f"{self.area_id}:{self.name}({self.water_level}m)"


class AlgorithmState:
    """
    Snapshot of the algorithm state at a discrete point in time.
    Stored in the simulation timeline for forward/backward replay.
    """
    def __init__(
        self,
        step_id: int,
        op_type: str,            # "DIVIDE", "COMPARE", "SELECT", "MERGE_ITEM", "MERGE_DONE"
        depth: int,
        active_range: tuple,     # (start_idx, end_idx)
        left_sub: List[AreaRecord],
        right_sub: List[AreaRecord],
        curr_left_idx: Optional[int] = None,
        curr_right_idx: Optional[int] = None,
        comp_left_val: Optional[float] = None,
        comp_right_val: Optional[float] = None,
        selected_item: Optional[AreaRecord] = None,
        comparison_text: str = "",
        why_text: str = "",
        merged_buffer: Optional[List[AreaRecord]] = None,
        array_snapshot: Optional[List[AreaRecord]] = None,
        comparisons_so_far: int = 0,
        merges_so_far: int = 0,
        explanation: str = "",
    ):
        self.step_id = step_id
        self.op_type = op_type
        self.depth = depth
        self.active_range = active_range
        self.left_sub = [copy.copy(x) for x in left_sub] if left_sub else []
        self.right_sub = [copy.copy(x) for x in right_sub] if right_sub else []
        self.curr_left_idx = curr_left_idx
        self.curr_right_idx = curr_right_idx
        self.comp_left_val = comp_left_val
        self.comp_right_val = comp_right_val
        self.selected_item = copy.copy(selected_item) if selected_item else None
        self.comparison_text = comparison_text
        self.why_text = why_text
        self.merged_buffer = [copy.copy(x) for x in merged_buffer] if merged_buffer else []
        self.array_snapshot = [copy.copy(x) for x in array_snapshot] if array_snapshot else []
        self.comparisons_so_far = comparisons_so_far
        self.merges_so_far = merges_so_far
        self.explanation = explanation


class TreeNode:
    """Represents a node in the visual Merge Sort recursion tree."""
    def __init__(self, node_id: int, start: int, end: int, depth: int, elements: List[AreaRecord]):
        self.node_id = node_id
        self.start = start
        self.end = end
        self.depth = depth
        self.elements = [copy.copy(x) for x in elements]
        self.left_child: Optional['TreeNode'] = None
        self.right_child: Optional['TreeNode'] = None
        self.state: str = "PENDING"  # "PENDING", "DIVIDED", "MERGING", "SORTED"


class MergeSortTracer:
    """
    Executes pure manual Merge Sort and generates an exhaustive,
    deterministic timeline of algorithm events.
    """
    def __init__(self, initial_data: List[AreaRecord]):
        self.original_data = [copy.copy(x) for x in initial_data]
        self.work_array = [copy.copy(x) for x in initial_data]
        self.timeline: List[AlgorithmState] = []
        self.comparisons_count = 0
        self.merges_count = 0
        self.step_counter = 0
        self.max_depth = 0
        self.tree_root: Optional[TreeNode] = None
        self._tree_node_counter = 0
        
        # Build tree structure and record timeline
        self._execute_and_trace()

    def _create_tree(self, start: int, end: int, depth: int) -> TreeNode:
        self._tree_node_counter += 1
        node = TreeNode(
            node_id=self._tree_node_counter,
            start=start,
            end=end,
            depth=depth,
            elements=self.work_array[start : end + 1],
        )
        if depth > self.max_depth:
            self.max_depth = depth

        if start < end:
            mid = (start + end) // 2
            node.left_child = self._create_tree(start, mid, depth + 1)
            node.right_child = self._create_tree(mid + 1, end, depth + 1)
        return node

    def _execute_and_trace(self):
        """Build recursion tree and execute manual merge sort with fine tracing."""
        self.tree_root = self._create_tree(0, len(self.work_array) - 1, depth=0)
        self._merge_sort_recursive(0, len(self.work_array) - 1, depth=0)

    def _merge_sort_recursive(self, start: int, end: int, depth: int):
        """
        Pure manual recursive merge sort.
        Divides array[start...end] in half, recursively sorts both halves,
        then merges them in descending order of water_level.
        """
        if start >= end:
            return

        mid = (start + end) // 2

        # 1. DIVIDE EVENT
        left_slice = self.work_array[start : mid + 1]
        right_slice = self.work_array[mid + 1 : end + 1]

        self.step_counter += 1
        div_state = AlgorithmState(
            step_id=self.step_counter,
            op_type="DIVIDE",
            depth=depth,
            active_range=(start, end),
            left_sub=left_slice,
            right_sub=right_slice,
            array_snapshot=self.work_array,
            comparisons_so_far=self.comparisons_count,
            merges_so_far=self.merges_count,
            explanation=f"DIVIDE: Split subarray of {end - start + 1} areas into [{start}..{mid}] ({len(left_slice)} items) and [{mid + 1}..{end}] ({len(right_slice)} items).",
            why_text="Divide and Conquer breaks the problem into subproblems until single-element arrays remain.",
        )
        self.timeline.append(div_state)

        # 2. RECURSE LEFT
        self._merge_sort_recursive(start, mid, depth + 1)

        # 3. RECURSE RIGHT
        self._merge_sort_recursive(mid + 1, end, depth + 1)

        # 4. MERGE THE TWO HALVES
        self._merge(start, mid, end, depth)

    def _merge(self, start: int, mid: int, end: int, depth: int):
        """
        Pure manual merge function.
        Compares elements from left and right halves and merges in DESCENDING order.
        """
        left_copy = [copy.copy(x) for x in self.work_array[start : mid + 1]]
        right_copy = [copy.copy(x) for x in self.work_array[mid + 1 : end + 1]]

        merged_buffer: List[AreaRecord] = []
        i = 0
        j = 0

        while i < len(left_copy) and j < len(right_copy):
            left_item = left_copy[i]
            right_item = right_copy[j]

            self.comparisons_count += 1
            left_val = left_item.water_level
            right_val = right_item.water_level

            # COMPARE STEP
            self.step_counter += 1
            comp_state = AlgorithmState(
                step_id=self.step_counter,
                op_type="COMPARE",
                depth=depth,
                active_range=(start, end),
                left_sub=left_copy,
                right_sub=right_copy,
                curr_left_idx=i,
                curr_right_idx=j,
                comp_left_val=left_val,
                comp_right_val=right_val,
                comparison_text=f"{left_item.name} ({left_val:.1f}m) vs {right_item.name} ({right_val:.1f}m)",
                why_text="Comparing flood levels. In descending sort, the area with the HIGHER water level has highest evacuation urgency.",
                merged_buffer=merged_buffer,
                array_snapshot=self.work_array,
                comparisons_so_far=self.comparisons_count,
                merges_so_far=self.merges_count,
                explanation=f"COMPARE: {left_item.area_id} ({left_val}m) vs {right_item.area_id} ({right_val}m).",
            )
            self.timeline.append(comp_state)

            # DESCENDING ORDER: Select larger water level
            if left_val >= right_val:
                chosen = left_item
                reason = f"{left_val:.1f}m >= {right_val:.1f}m: {left_item.name} has higher flood level, placing it first."
                i += 1
            else:
                chosen = right_item
                reason = f"{right_val:.1f}m > {left_val:.1f}m: {right_item.name} has higher flood level, placing it first."
                j += 1

            merged_buffer.append(chosen)

            # SELECT & INSERT STEP
            self.step_counter += 1
            sel_state = AlgorithmState(
                step_id=self.step_counter,
                op_type="SELECT",
                depth=depth,
                active_range=(start, end),
                left_sub=left_copy,
                right_sub=right_copy,
                curr_left_idx=i - 1 if chosen is left_item else i,
                curr_right_idx=j - 1 if chosen is right_item else j,
                selected_item=chosen,
                comparison_text=f"Selected {chosen.name} ({chosen.water_level:.1f}m)",
                why_text=reason,
                merged_buffer=merged_buffer,
                array_snapshot=self.work_array,
                comparisons_so_far=self.comparisons_count,
                merges_so_far=self.merges_count,
                explanation=f"SELECT: Added {chosen.area_id} ({chosen.name}) to merged list.",
            )
            self.timeline.append(sel_state)

        # Collect remaining elements from left subarray
        while i < len(left_copy):
            rem_item = left_copy[i]
            merged_buffer.append(rem_item)
            i += 1
            self.step_counter += 1
            self.timeline.append(
                AlgorithmState(
                    step_id=self.step_counter,
                    op_type="MERGE_ITEM",
                    depth=depth,
                    active_range=(start, end),
                    left_sub=left_copy,
                    right_sub=right_copy,
                    selected_item=rem_item,
                    comparison_text=f"Append remaining: {rem_item.name} ({rem_item.water_level:.1f}m)",
                    why_text="Right subarray exhausted. Appending remaining sorted elements from left half.",
                    merged_buffer=merged_buffer,
                    array_snapshot=self.work_array,
                    comparisons_so_far=self.comparisons_count,
                    merges_so_far=self.merges_count,
                    explanation=f"COLLECT: Appended remaining {rem_item.area_id} to buffer.",
                )
            )

        # Collect remaining elements from right subarray
        while j < len(right_copy):
            rem_item = right_copy[j]
            merged_buffer.append(rem_item)
            j += 1
            self.step_counter += 1
            self.timeline.append(
                AlgorithmState(
                    step_id=self.step_counter,
                    op_type="MERGE_ITEM",
                    depth=depth,
                    active_range=(start, end),
                    left_sub=left_copy,
                    right_sub=right_copy,
                    selected_item=rem_item,
                    comparison_text=f"Append remaining: {rem_item.name} ({rem_item.water_level:.1f}m)",
                    why_text="Left subarray exhausted. Appending remaining sorted elements from right half.",
                    merged_buffer=merged_buffer,
                    array_snapshot=self.work_array,
                    comparisons_so_far=self.comparisons_count,
                    merges_so_far=self.merges_count,
                    explanation=f"COLLECT: Appended remaining {rem_item.area_id} to buffer.",
                )
            )

        # Copy back to main work_array slice
        self.merges_count += 1
        for k in range(len(merged_buffer)):
            self.work_array[start + k] = copy.copy(merged_buffer[k])

        self.step_counter += 1
        done_state = AlgorithmState(
            step_id=self.step_counter,
            op_type="MERGE_DONE",
            depth=depth,
            active_range=(start, end),
            left_sub=left_copy,
            right_sub=right_copy,
            merged_buffer=merged_buffer,
            array_snapshot=self.work_array,
            comparisons_so_far=self.comparisons_count,
            merges_so_far=self.merges_count,
            explanation=f"MERGE COMPLETE: Subarray [{start}..{end}] ({len(merged_buffer)} items) is now sorted descending.",
            why_text="Both sorted halves have been merged into a single sorted subarray.",
        )
        self.timeline.append(done_state)

    def get_final_sorted(self) -> List[AreaRecord]:
        return [copy.copy(x) for x in self.work_array]
