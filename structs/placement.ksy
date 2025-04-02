    
meta:
  endian: le
  bit-endian: le
  id: pla
  file-extension: pla

seq:
  - {id: header, type: base_header}

instances:
  tracks:
    {pos: 0x10, type: track, repeat: expr, repeat-expr: header.num_tracks}

types:
  base_header:
    seq:
      - {id: magic, contents: [0x50, 0x4c, 0x41, 0x00]}
      - {id: version, type: u2}
      - {id: num_tracks, type: u2}
      - {id: dti_table_offset, type: u4}
      - {id: name_offset, type: u4}
  
  track:
    seq:
      - {id: type, type: u4}
      - {id: prop_type, type: u4}
      - {id: parent, type: u4}
      - {id: move_line, type: u4}
      - {id: class_ofs, type: u4}
      - {id: dti_ref, type: u4}
      - {id: data_ref, type: u4}
    instances:
      size_:
        value: 0x1C
      name:
        pos: class_ofs + _root.header.name_offset
        type: str
        encoding: utf-8
        terminator: 0
      data:
        if: data_ref > 0 and type > 5
        pos: data_ref
        type:
          switch-on: type
          cases:
            6: u4
            7: u4
            8: u4
            9: u4
            10: u4
            11: resource
            

  resource:
    seq:
      - {id: ref_ofs, type: u4}
    instances:
      ref_dti:
        pos: ref_ofs + _root.header.name_offset
        type: u4
      ref_path:
        pos: ref_ofs + _root.header.name_offset + 4
        type: str
        encoding: utf-8
        terminator: 0
        
  vec3:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      
  vec4:
    seq:
      - {id: x, type: f4}
      - {id: y, type: f4}
      - {id: z, type: f4}
      - {id: w, type: f4}
      
  color:
    seq:
      - {id: r, type: f4}
      - {id: g, type: f4}
      - {id: b, type: f4}
      - {id: a, type: f4}
  
  point:
    seq:
      - {id: x, type: s4}
      - {id: y, type: s4}
      
  size:
    seq:
      - {id: w, type: s4}
      - {id: h, type: s4}
      
  rect:
    seq:
      - {id: l, type: s4}
      - {id: t, type: s4}
      - {id: r, type: s4}
      - {id: b, type: s4}

  mat3x3:
    seq:
      - {id: r0, type: vec3}
      - {id: r1, type: vec3}
      - {id: r2, type: vec3}
      
  mat4x3:
    seq:
      - {id: r0, type: vec3}
      - {id: r1, type: vec3}
      - {id: r2, type: vec3}
      - {id: r3, type: vec3}
      
  mat4x4:
    seq:
      - {id: r0, type: vec4}
      - {id: r1, type: vec4}
      - {id: r2, type: vec4}
      - {id: r3, type: vec4}