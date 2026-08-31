
The goal here is to convert `.save` file to json file.
That file we should easily read and navigate in other applications.

Using native format of the file would make sense only if 
we would need to save it back. 
Otherwise, keeping it natively would require us to implement 
an enormous amount of functionality to work on native data.
But we don't even need most of it probably, just certain pieces of data:
ownership of provinces and regions.

Links:
Rusted parser of esf.
https://github.com/Frodo45127/rpfm/blob/master/rpfm_lib/src/files/esf/mod.rs#L135