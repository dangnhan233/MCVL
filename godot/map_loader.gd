extends Node2D
## Nạp layout.json của một map: dựng TileMapLayer + các vật thể (Sprite2D, gốc ở chân vật thể)
## và một Camera2D để nhìn được toàn bộ bản đồ (map lớn hơn màn hình 240x320).
## Dùng: gắn script vào node gốc của maps/map_XX/map.tscn (đã gắn sẵn).
##
## Điều khiển xem map: kéo ngón tay / chuột, hoặc phím mũi tên.

@export var map_id: int = 1
@export var pan_speed: float = 160.0

const DEFAULT_TILE := 16

var _cam: Camera2D
var _ready_ok := false
var _dragging := false


func _ready() -> void:
	var dir := "res://maps/map_%02d" % map_id
	var path := dir + "/layout.json"

	if not FileAccess.file_exists(path):
		push_error("MCVL: không tìm thấy " + path)
		return
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("MCVL: không mở được %s (lỗi %d)" % [path, FileAccess.get_open_error()])
		return
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("MCVL: layout.json sai định dạng: " + path)
		return
	var data: Dictionary = parsed

	# JSON luôn trả số thực (float) -> ép về int tường minh.
	var w: int = int(data.get("width", 0))
	var h: int = int(data.get("height", 0))
	var tile: int = int(data.get("tile_size", DEFAULT_TILE))
	var arr: Array = data.get("ground", [])
	if w <= 0 or h <= 0 or arr.size() < w * h:
		push_error("MCVL: kích thước/ground không khớp (w=%d h=%d n=%d)" % [w, h, arr.size()])
		return

	var ground := get_node_or_null("Ground") as TileMapLayer
	if ground == null:
		push_error("MCVL: thiếu node Ground (TileMapLayer)")
		return
	var holder := get_node_or_null("Objects") as Node2D
	if holder == null:
		holder = Node2D.new()
		holder.name = "Objects"
		holder.y_sort_enabled = true
		add_child(holder)

	# --- Nền ---
	for i in range(w * h):
		var cy: int = floori(float(i) / float(w))
		ground.set_cell(Vector2i(i % w, cy), 0, Vector2i(int(arr[i]), 0))

	# --- Vật thể (gốc ở chân/giữa đáy) ---
	var missing := 0
	for o in data.get("objects", []):
		var od: Dictionary = o
		var tpath: String = dir + "/objects/" + String(od["file"])
		if not ResourceLoader.exists(tpath):
			missing += 1
			continue
		var tex := load(tpath) as Texture2D
		if tex == null:
			missing += 1
			continue
		var s := Sprite2D.new()
		s.texture = tex
		s.centered = false
		s.offset = Vector2(-tex.get_width() / 2.0, -tex.get_height())
		s.position = Vector2(float(od["x"]), float(od["y"]))
		holder.add_child(s)
	if missing > 0:
		push_warning("MCVL: map %d thiếu %d ảnh vật thể" % [map_id, missing])

	# Ô chặn đường (nước): data["blocked"] cùng kích thước với data["ground"].

	# --- Camera: đặt tại điểm spawn, bị giới hạn trong phạm vi bản đồ ---
	var spawn_arr: Array = data.get("spawn", [w * tile * 0.5, h * tile * 0.5])
	var spawn := Vector2(float(spawn_arr[0]), float(spawn_arr[1]))
	_cam = Camera2D.new()
	_cam.limit_left = 0
	_cam.limit_top = 0
	_cam.limit_right = w * tile
	_cam.limit_bottom = h * tile
	_cam.position = spawn
	add_child(_cam)
	_cam.make_current()
	_ready_ok = true


func _process(delta: float) -> void:
	if not _ready_ok:
		return
	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if dir != Vector2.ZERO:
		_cam.position += dir * pan_speed * delta


func _unhandled_input(event: InputEvent) -> void:
	if not _ready_ok:
		return
	if event is InputEventScreenTouch:
		_dragging = event.pressed
	elif event is InputEventScreenDrag:
		_cam.position -= event.relative
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		_dragging = event.pressed
	elif event is InputEventMouseMotion and _dragging:
		_cam.position -= event.relative
