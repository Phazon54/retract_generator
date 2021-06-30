pillar_radius = 2
pillar_height = 10

pillar_distance = 15

base_height = 0.6

pillar = cylinder(pillar_radius,pillar_height)

base = cube(pillar_distance+pillar_radius*2,pillar_radius*2,base_height)

part = union{
  base,
  translate(-pillar_distance/2,0,base_height)*pillar,
  translate(pillar_distance/2,0,base_height)*pillar,
}

emit(part)
